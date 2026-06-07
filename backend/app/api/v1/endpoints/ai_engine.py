from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.challenge import Challenge as ChallengeModel, DifficultyLevel as DifficultyEnum, ChallengeStatus
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService
from app.services.challenge_service import ChallengeService
from app.utils.auth import get_current_user, get_current_admin_user
from app.schemas.challenge import ChallengeResponse
from pathlib import Path
from pydantic import BaseModel
import random
import uuid
import json

router = APIRouter()


class ChallengeGenerationRequest(BaseModel):
    category: str
    difficulty: str
    topic: str
    learning_objectives: List[str]
    user_skill_level: str


class AIHintRequest(BaseModel):
    challenge_id: int
    user_progress: Dict[str, Any]
    hint_level: int = 1


class AIFeedbackRequest(BaseModel):
    challenge_id: int
    user_attempt: str
    is_correct: bool


class ChatbotRequest(BaseModel):
    message: str
    challenge_id: int | None = None
    conversation_history: List[Dict[str, str]] = []
    user_skill_level: str = "beginner"


class ProactiveTipRequest(BaseModel):
    context: str = "encouragement"  # stuck_long_time, multiple_failures, first_challenge, encouragement
    challenge_id: int | None = None


class PublicChallengeGenerationRequest(BaseModel):
    category: str        # e.g. "cryptography", "web", "forensics"
    difficulty: str      # beginner / easy / medium / hard / expert
    topic: str           # free text topic hint


class PersonalizedChallengeRequest(BaseModel):
    # Make fields optional with sensible defaults so generation still works
    category: Optional[str] = "mixed"
    difficulty: Optional[str] = "beginner"
    learning_goal: Optional[str] = "Learn base64 decoding"


class GeneratedChallengeResponse(ChallengeResponse):
    """Alias for clarity in OpenAPI docs"""
    pass


# ---------- Map template titles to running challenge app ports + flags ----------
# Each entry: keyword (lowercase) -> (port, flag_in_app)
_TEMPLATE_PORT_MAP = {
    "caesar":   (8081, "FLAG{caesar_was_here}"),
    "base64":   (8086, "FLAG{base64_decoding_rocks}"),
    "xor":      (8086, "FLAG{base64_decoding_rocks}"),   # reuse base64 app
    "decoder":  (8086, "FLAG{base64_decoding_rocks}"),
    "login":    (8080, "FLAG{sql_injection_master}"),
    "sql":      (8080, "FLAG{sql_injection_master}"),
    "reflected":(8085, "FLAG{xss_1s_ev3rywh3re}"),
    "xss":      (8085, "FLAG{xss_1s_ev3rywh3re}"),
    "hidden":   (8082, "FLAG{steganography_rocks}"),
    "steg":     (8082, "FLAG{steganography_rocks}"),
    "magic":    (8084, "FLAG{forensics_recovery_expert}"),
    "file":     (8084, "FLAG{forensics_recovery_expert}"),
    "packet":   (8083, "FLAG{wireshark_wizard}"),
    "network":  (8083, "FLAG{wireshark_wizard}"),
    "strings":  (8084, "FLAG{forensics_recovery_expert}"),
    "cookie":   (8087, "FLAG{cookies_are_not_secure}"),
}

def _get_port_and_flag_for_challenge(title: str, category_key: str):
    """Return (docker_port, flag) for a generated challenge based on title/category.
    Only match against the part before ' — ' to avoid matching the learning goal suffix."""
    # Use only the template name (before the em-dash suffix)
    short_title = title.split("—")[0].split("\u2014")[0].strip().lower()
    for keyword, (port, flag) in _TEMPLATE_PORT_MAP.items():
        if keyword in short_title:
            return port, flag
    # category fallback
    category_fallbacks = {
        "cryptography": (8081, "FLAG{caesar_was_here}"),
        "web":          (8085, "FLAG{xss_1s_ev3rywh3re}"),
        "forensics":    (8082, "FLAG{steganography_rocks}"),
        "network":      (8083, "FLAG{wireshark_wizard}"),
        "binary":       (8084, "FLAG{forensics_recovery_expert}"),
    }
    return category_fallbacks.get(category_key, (8086, "FLAG{base64_decoding_rocks}"))


# ---------- Challenge template bank (fallback when Ollama is offline) ----------
_CHALLENGE_TEMPLATES = {
    "cryptography": [
        {
            "title": "Caesar's Secret",
            "desc": "A message has been encrypted using a classic Roman cipher. "
                    "Decrypt the following: {cipher}",
            "short": "Decrypt a Caesar cipher to reveal the hidden flag.",
            "flag_word": "HIDDEN",
            "hints": [
                "The Romans shifted letters by a fixed amount.",
                "Try all 25 possible shifts — one of them will make sense.",
                "The flag starts with FLAG{ after decryption."
            ],
            "tags": ["caesar", "classical-crypto", "rotation"],
            "objectives": ["Understand substitution ciphers", "Practice brute-force decryption"],
            "points_map": {"beginner": 50, "easy": 75, "medium": 100, "hard": 150, "expert": 200},
        },
        {
            "title": "Base64 Bonanza",
            "desc": "Someone encoded a secret message using a common web encoding scheme. "
                    "Decode the following payload to find the flag:\n{cipher}",
            "short": "Decode a Base64-encoded string to get the flag.",
            "flag_word": "ENCODED",
            "hints": [
                "The string ends with '==' padding — a classic sign.",
                "Python: import base64; base64.b64decode(s)",
                "It's encoding, not encryption — no key required."
            ],
            "tags": ["base64", "encoding", "easy-win"],
            "objectives": ["Understand Base64 encoding", "Use decoding tools effectively"],
            "points_map": {"beginner": 40, "easy": 60, "medium": 80, "hard": 120, "expert": 160},
        },
        {
            "title": "XOR Chaos",
            "desc": "The flag has been XOR'd with a single-byte key and hex-encoded. "
                    "Recover the flag from: {cipher}",
            "short": "Reverse a single-byte XOR cipher.",
            "flag_word": "XORSECRET",
            "hints": [
                "XOR with the same key twice returns the original — try all 256 keys.",
                "The flag format starts with FLAG{ — use that to narrow the key.",
                "Python: bytes([b ^ key for b in bytes.fromhex(s)])"
            ],
            "tags": ["xor", "brute-force", "hex"],
            "objectives": ["Understand XOR cipher", "Implement brute-force key search"],
            "points_map": {"beginner": 60, "easy": 90, "medium": 130, "hard": 180, "expert": 250},
        },
    ],
    "web": [
        {
            "title": "Login Bypass",
            "desc": "A login form lacks proper input sanitization. "
                    "Find a way to authenticate without valid credentials.",
            "short": "Exploit a vulnerable login form to bypass authentication.",
            "flag_word": "SQLMASTER",
            "hints": [
                "What happens if you add a single quote to the username field?",
                "Think about how the SQL query is constructed on the backend.",
                "Try: admin' --  as the username with any password."
            ],
            "tags": ["sqli", "authentication", "web"],
            "objectives": ["Understand SQL injection", "Bypass authentication controls"],
            "points_map": {"beginner": 75, "easy": 100, "medium": 150, "hard": 200, "expert": 300},
        },
        {
            "title": "Reflected Mayhem",
            "desc": "A search page reflects user input without sanitization. "
                    "Execute JavaScript in the victim's browser to capture the flag.",
            "short": "Exploit a reflected XSS vulnerability.",
            "flag_word": "XSSWIN",
            "hints": [
                "Try injecting <b>test</b> — does the HTML render?",
                "If so, try <script>alert(1)</script>.",
                "Event handlers like onerror can bypass script-tag filters."
            ],
            "tags": ["xss", "reflected", "client-side"],
            "objectives": ["Understand XSS", "Identify and exploit reflected injection points"],
            "points_map": {"beginner": 75, "easy": 100, "medium": 150, "hard": 200, "expert": 300},
        },
    ],
    "forensics": [
        {
            "title": "Hidden in Plain Sight",
            "desc": "A PNG file contains a hidden message. Extract the flag "
                    "from the image metadata or steganographic layer.",
            "short": "Find a hidden flag using image forensics tools.",
            "flag_word": "STEGMASTER",
            "hints": [
                "Run exiftool on the file — metadata can hide secrets.",
                "Try steghide extract -sf image.png",
                "Check the least-significant bits with zsteg or stegsolve."
            ],
            "tags": ["steganography", "image", "metadata"],
            "objectives": ["Use forensic tools", "Understand steganographic techniques"],
            "points_map": {"beginner": 60, "easy": 80, "medium": 120, "hard": 170, "expert": 230},
        },
        {
            "title": "Magic Bytes",
            "desc": "A file has been given a wrong extension to hide its true type. "
                    "Identify the real format and extract the flag within.",
            "short": "Use file signature analysis to reveal a disguised file.",
            "flag_word": "FILEDETECTIVE",
            "hints": [
                "Run 'file suspicious.dat' — it checks magic bytes, not the extension.",
                "Hex editors like xxd or HxD show the raw file header.",
                "Common headers: FF D8 FF = JPEG, 89 50 4E 47 = PNG, 50 4B 03 04 = ZIP"
            ],
            "tags": ["file-forensics", "magic-bytes", "hex"],
            "objectives": ["Identify file types by magic bytes", "Use hex editors"],
            "points_map": {"beginner": 50, "easy": 70, "medium": 110, "hard": 160, "expert": 220},
        },
    ],
    "network": [
        {
            "title": "Packet Hunt",
            "desc": "A PCAP capture contains credentials transmitted in cleartext. "
                    "Analyse the traffic and extract the flag.",
            "short": "Analyse a packet capture to find transmitted credentials.",
            "flag_word": "WIRESNIFFER",
            "hints": [
                "Open the file in Wireshark and filter for http.",
                "Follow the TCP stream on the interesting HTTP request.",
                "Look for POST requests — they often carry login data."
            ],
            "tags": ["wireshark", "pcap", "cleartext"],
            "objectives": ["Use Wireshark", "Analyse HTTP traffic", "Identify sensitive data in transit"],
            "points_map": {"beginner": 60, "easy": 85, "medium": 125, "hard": 175, "expert": 240},
        },
    ],
    "binary": [
        {
            "title": "Strings Are Your Friend",
            "desc": "A compiled binary contains a hard-coded flag. "
                    "Find it without running the binary.",
            "short": "Extract a hard-coded flag from a binary using static analysis.",
            "flag_word": "STATICANALYSIS",
            "hints": [
                "Run 'strings binary | grep FLAG' for a quick win.",
                "Ghidra or radare2 can decompile the binary for deeper analysis.",
                "Hard-coded strings live in the .rodata / .data sections."
            ],
            "tags": ["reversing", "strings", "static-analysis"],
            "objectives": ["Use strings tool", "Understand ELF binary structure"],
            "points_map": {"beginner": 50, "easy": 75, "medium": 110, "hard": 160, "expert": 220},
        },
    ],
    "misc": [
        {
            "title": "Decoder Ring",
            "desc": "A strange sequence of numbers has been intercepted: {cipher}. "
                    "Decode it to reveal the flag.",
            "short": "Decode a multi-layer encoded message.",
            "flag_word": "DECODER",
            "hints": [
                "Start by identifying the encoding — is it decimal ASCII? Hex? Binary?",
                "Convert numbers to ASCII characters: chr(72) = 'H'.",
                "If that doesn't work, try hex then ASCII."
            ],
            "tags": ["encoding", "ascii", "multi-layer"],
            "objectives": ["Identify encoding schemes", "Implement multi-step decoding"],
            "points_map": {"beginner": 40, "easy": 60, "medium": 90, "hard": 130, "expert": 180},
        },
    ],
}

# Category name → category_id mapping (matches DB seed data)
_CATEGORY_IDS = {
    "cryptography": 1,
    "web": 2,
    "forensics": 3,
    "network": 4,
    "binary": 5,
    "misc": 6,
}


def _make_caesar_cipher(plaintext: str, shift: int) -> str:
    result = []
    for c in plaintext:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result.append(chr((ord(c) - base + shift) % 26 + base))
        else:
            result.append(c)
    return ''.join(result)


def _generate_challenge_data(category: str, difficulty: str, topic: str) -> Dict[str, Any]:
    """Build a concrete challenge dict from templates."""
    cat_key = category.lower().split()[0]
    if cat_key not in _CHALLENGE_TEMPLATES:
        cat_key = "misc"

    template = random.choice(_CHALLENGE_TEMPLATES[cat_key])
    flag_suffix = template["flag_word"]
    flag = f"FLAG{{{flag_suffix}_{uuid.uuid4().hex[:6].upper()}}}"

    # Build the cipher text shown in the description
    if "{cipher}" in template["desc"]:
        if cat_key == "cryptography" and "Caesar" in template["title"]:
            shift = random.randint(3, 20)
            cipher = _make_caesar_cipher(f"The flag is: {flag}", shift)
        elif cat_key == "cryptography" and "XOR" in template["title"]:
            key = random.randint(1, 255)
            cipher = bytes([b ^ key for b in flag.encode()]).hex()
        elif cat_key == "cryptography":
            import base64
            cipher = base64.b64encode(flag.encode()).decode()
        else:
            cipher = flag.encode().hex()
        description = template["desc"].replace("{cipher}", f"`{cipher}`")
    else:
        description = template["desc"]

    # Personalise title with topic if provided
    title = template["title"]
    if topic:
        title = f"{title} — {topic.title()[:40]}"

    # Avoid duplicate slugs
    slug_base = title.lower()
    for ch in ' —/\\()[]{}:;,!?':
        slug_base = slug_base.replace(ch, '-')
    import re as _re
    slug_base = _re.sub(r'-+', '-', slug_base).strip('-')
    slug = f"{slug_base}-{uuid.uuid4().hex[:4]}"

    points = template["points_map"].get(difficulty, 100)

    return {
        "title": title,
        "slug": slug,
        "description": description,
        "short_description": template["short"],
        "category_id": _CATEGORY_IDS.get(cat_key, 6),
        "difficulty": difficulty,
        "points": points,
        "flag": flag,
        "hints": json.dumps(template["hints"]),
        "tags": json.dumps(template["tags"]),
        "learning_objectives": json.dumps(template["objectives"]),
        "generated_by_ai": True,
    }


_USER_CATEGORY_MAP = {
    "crypto": "cryptography",
    "cryptography": "cryptography",
    "web": "web",
    "forensics": "forensics",
    "reverse engineering": "binary",
    "reversing": "binary",
    "network": "network",
    "mixed": "mixed",
}


def _normalize_category_input(category: str) -> str:
    key = (category or "").strip().lower()
    return _USER_CATEGORY_MAP.get(key, key or "mixed")


def _determine_personalized_category(
    requested_category: str,
    user: UserModel,
    db: Session
) -> str:
    """
    Pick a target category based on user weaknesses when 'mixed' is requested.
    Falls back to cryptography if nothing else is available.
    """
    cat_key = _normalize_category_input(requested_category)
    if cat_key != "mixed":
        return cat_key

    analytics_service = AnalyticsService(db)
    # Make sure analytics and category_performance are up to date
    analytics = analytics_service.update_user_analytics(user.id)

    # Prefer weakest category from analytics.category_performance if available
    weakest_category: Optional[str] = None
    if analytics and analytics.category_performance:
        try:
            perf = json.loads(analytics.category_performance)
            worst_rate = 2.0  # >100%
            for name, data in perf.items():
                attempts = data.get("attempts", 0) or 0
                solved = data.get("solved", 0) or 0
                if attempts == 0:
                    continue
                rate = solved / attempts
                if rate < worst_rate:
                    worst_rate = rate
                    weakest_category = name.lower()
        except (ValueError, json.JSONDecodeError):
            weakest_category = None

    if weakest_category:
        for user_label, internal_key in _USER_CATEGORY_MAP.items():
            if weakest_category.startswith(user_label):
                return internal_key

    # Fallback to cryptography as a generally good teaching area
    return "cryptography"


def _map_user_skill_to_difficulty(user: UserModel, requested_difficulty: str) -> str:
    """Blend user skill_level and requested difficulty into a challenge difficulty string."""
    req = (requested_difficulty or "").strip().lower()
    if req in {"beginner", "easy", "medium", "hard", "expert"}:
        base = req
    else:
        base = "beginner"

    skill = (user.skill_level or "beginner").lower()

    # Simple heuristic: nudge difficulty up/down based on skill
    order = ["beginner", "easy", "medium", "hard", "expert"]
    idx = order.index(base)

    if skill in {"advanced", "expert"} and idx < len(order) - 1:
        idx += 1
    elif skill == "beginner" and idx > 0:
        idx = max(0, idx - 1)

    return order[idx]


def _ensure_generated_static_dir() -> Path:
    base_static = Path(__file__).resolve().parents[4] / "static" / "challenges" / "generated"
    base_static.mkdir(parents=True, exist_ok=True)
    return base_static


def _create_challenge_file(
    challenge_data: Dict[str, Any],
    category_key: str
) -> Optional[str]:
    """
    Create a downloadable resource file for certain categories.
    Returns a URL path (e.g. /static/challenges/generated/xyz.txt) or None.
    """
    generated_dir = _ensure_generated_static_dir()

    title_slug = challenge_data.get("slug") or f"challenge-{uuid.uuid4().hex[:6]}"
    ext = ".txt"

    if category_key == "cryptography":
        ext = ".txt"
        filename = f"{title_slug}-crypto{ext}"
        content = (
            "You intercepted an encoded message.\n\n"
            "Use your cryptography skills to recover the flag.\n\n"
            f"{challenge_data.get('description', '')}\n"
        )
    elif category_key == "forensics":
        ext = ".txt"
        filename = f"{title_slug}-forensics{ext}"
        content = (
            "A suspicious file was recovered from a compromised system.\n\n"
            "Your job is to analyze it and recover any hidden secrets.\n\n"
            f"{challenge_data.get('description', '')}\n"
        )
    else:
        return None

    file_path = generated_dir / filename
    file_path.write_text(content, encoding="utf-8")
    return f"/static/challenges/generated/{filename}"


@router.post("/admin/generate-challenge-task")
async def generate_challenge_task(
    request: ChallengeGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Generate a new challenge using AI (admin only, background task placeholder)"""
    ai_service = AIService(db)

    # Start background task for challenge generation
    task_id = ai_service.start_challenge_generation_task(
        category=request.category,
        difficulty=request.difficulty,
        topic=request.topic,
        learning_objectives=request.learning_objectives,
        user_skill_level=request.user_skill_level,
        created_by=current_user.id
    )

    return {
        "message": "Challenge generation started",
        "task_id": task_id,
        "estimated_time": "2-5 minutes"
    }


@router.post(
    "/generate-challenge",
    response_model=GeneratedChallengeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_personalized_challenge(
    request: PersonalizedChallengeRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Generate a personalized challenge for the current user.

    - Analyses user skill level and category weaknesses
    - Creates a new Challenge row marked as generated_by_ai
    - Assigns it to the user via generated_for_user_id
    - Optionally creates a downloadable file under /static/challenges/generated
    """
    challenge_service = ChallengeService(db)

    # Fall back to defaults if the client did not send specific values
    requested_category = request.category or "mixed"
    requested_difficulty = request.difficulty or "beginner"
    learning_goal = request.learning_goal or "Learn base64 decoding"

    category_key = _determine_personalized_category(requested_category, current_user, db)
    difficulty = _map_user_skill_to_difficulty(current_user, requested_difficulty)

    # Build base challenge data from templates (purely server-side, no flag leak in API)
    base_data = _generate_challenge_data(category_key, difficulty, learning_goal)

    # Attach file resource when appropriate
    files_url = _create_challenge_file(base_data, category_key)

    # Map to ORM model
    difficulty_enum = DifficultyEnum[difficulty.upper()] if difficulty.upper() in DifficultyEnum.__members__ else DifficultyEnum.BEGINNER

    docker_port, app_flag = _get_port_and_flag_for_challenge(base_data["title"], category_key)

    challenge = ChallengeModel(
        title=base_data["title"],
        slug=base_data["slug"],
        description=base_data["description"],
        short_description=base_data["short_description"],
        category_id=base_data["category_id"],
        difficulty=difficulty_enum,
        points=base_data["points"],
        estimated_time=30,
        flag=app_flag,
        hints=base_data["hints"],
        solution=None,
        writeup=None,
        files_url=files_url,
        docker_image=None,
        docker_port=docker_port,
        container_config=None,
        tags=base_data["tags"],
        learning_objectives=base_data["learning_objectives"],
        status="ACTIVE",
        generated_by_ai=True,
        ai_model_used="template-engine",
        generation_prompt=learning_goal,
        generated_for_user_id=current_user.id,
    )

    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    return challenge


@router.get("/generation-status/{task_id}")
async def get_generation_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get status of challenge generation task"""
    ai_service = AIService(db)
    status_data = ai_service.get_generation_task_status(task_id)

    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return status_data


@router.get(
    "/generated-challenges",
    response_model=list[GeneratedChallengeResponse],
)
async def get_user_generated_challenges(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Return all challenges that were generated by AI specifically for this user.
    Flags and solutions are not exposed in the API response.
    """
    challenges = (
        db.query(ChallengeModel)
        .filter(
            ChallengeModel.generated_by_ai.is_(True),
            ChallengeModel.generated_for_user_id == current_user.id,
        )
        .order_by(ChallengeModel.created_at.desc())
        .all()
    )
    return challenges


@router.post("/hint")
async def get_ai_hint(
    request: AIHintRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get AI-generated hint for a challenge"""
    ai_service = AIService(db)

    hint = await ai_service.generate_personalized_hint(
        user_id=current_user.id,
        challenge_id=request.challenge_id,
        user_progress=request.user_progress,
        hint_level=request.hint_level
    )

    if not hint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unable to generate hint"
        )

    return {"hint": hint, "level": request.hint_level, "is_ai_generated": True}


@router.post("/feedback")
async def get_ai_feedback(
    request: AIFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get AI-generated feedback on user's attempt"""
    ai_service = AIService(db)

    feedback = await ai_service.generate_feedback(
        user_id=current_user.id,
        challenge_id=request.challenge_id,
        user_attempt=request.user_attempt,
        is_correct=request.is_correct
    )

    return {"feedback": feedback, "is_ai_generated": True}


@router.get("/skill-assessment")
async def get_skill_assessment(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get AI-based skill assessment for the user"""
    ai_service = AIService(db)

    assessment = await ai_service.assess_user_skills(current_user.id)
    return assessment


@router.post("/adaptive-difficulty")
async def adjust_difficulty(
    challenge_id: int,
    performance_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get difficulty adjustment recommendations based on performance"""
    ai_service = AIService(db)

    recommendations = await ai_service.recommend_difficulty_adjustment(
        user_id=current_user.id,
        challenge_id=challenge_id,
        performance_data=performance_data
    )

    return recommendations


@router.get("/learning-path")
async def get_learning_path(
    target_skill: str = "intermediate",
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get AI-generated personalized learning path"""
    ai_service = AIService(db)

    learning_path = await ai_service.generate_learning_path(
        user_id=current_user.id,
        target_skill=target_skill
    )

    return learning_path


@router.post("/chatbot")
async def chatbot_conversation(
    request: ChatbotRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """AI chatbot for general CTF assistance and concept explanations"""
    ai_service = AIService(db)

    # Use the smart chatbot response that works with or without Ollama
    result = await ai_service.smart_chatbot_response(
        message=request.message,
        challenge_id=request.challenge_id,
        user_skill_level=current_user.skill_level or request.user_skill_level,
        conversation_history=request.conversation_history
    )

    # Add contextual suggestions based on response type
    suggestions = {
        "hint": ["Give me another hint", "Explain the concept", "What tools should I use?"],
        "explanation": ["Tell me more", "Give me an example", "How do I practice this?"],
        "tools": ["How do I use these?", "Any beginner tips?", "Give me a hint"],
        "encouragement": ["Give me a hint", "Explain the challenge type", "What should I try?"],
        "guidance": ["I tried that, what's next?", "Explain more", "Give me a stronger hint"],
        "greeting": ["Explain cryptography", "What tools do I need?", "Help with a challenge"],
        "ai_response": ["Tell me more", "Give me a hint", "What tools should I use?"],
        "clarification": ["I'm working on crypto", "Help with web challenges", "Forensics help"]
    }

    return {
        "response": result["response"],
        "is_ai_generated": result.get("is_ai_generated", False),
        "type": result.get("type", "general"),
        "suggestions": suggestions.get(result.get("type", "general"), ["Ask me anything"])
    }


@router.post("/proactive-tip")
async def get_proactive_tip(
    request: ProactiveTipRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get a proactive tip/popup message for the user"""
    ai_service = AIService(db)

    tip = ai_service.get_proactive_tip(request.context)

    # If challenge context provided, add relevant guidance
    challenge_hint = None
    if request.challenge_id:
        from app.services.challenge_service import ChallengeService
        challenge_service = ChallengeService(db)
        challenge = challenge_service.get_challenge_by_id(request.challenge_id)
        if challenge and challenge.category:
            challenge_hint = ai_service.get_smart_hint(
                challenge.category.name,
                challenge.title,
                1
            )

    return {
        "tip": tip,
        "challenge_hint": challenge_hint,
        "context": request.context,
        "show_as_popup": True
    }


@router.get("/smart-hint/{challenge_id}")
async def get_smart_hint(
    challenge_id: int,
    hint_level: int = 1,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get a smart contextual hint for a challenge"""
    ai_service = AIService(db)

    from app.services.challenge_service import ChallengeService
    challenge_service = ChallengeService(db)
    challenge = challenge_service.get_challenge_by_id(challenge_id)

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    category_name = challenge.category.name if challenge.category else "misc"
    hint = ai_service.get_smart_hint(category_name, challenge.title, hint_level)

    return {
        "hint": hint,
        "level": hint_level,
        "challenge_id": challenge_id,
        "has_more_hints": hint_level < 4
    }


@router.get("/models/status")
async def get_ai_models_status():
    """Get status of AI models - no auth required for status check"""
    try:
        ai_service = AIService()
        models_status = ai_service.get_models_status()
        return models_status
    except Exception as e:
        # If Ollama is not running, return offline status
        return {
            "status": "offline",
            "message": "AI service (Ollama) is not running",
            "available_models": [],
            "recommendation": "Install Ollama from https://ollama.ai and run: ollama pull llama3"
        }