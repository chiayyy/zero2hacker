from sqlalchemy.orm import Session
from app.core.config import settings
from typing import Dict, Any, List, Optional
import httpx
import json
import uuid
import random
from datetime import datetime


# Smart hint templates that guide without giving answers
HINT_TEMPLATES = {
    "cryptography": {
        "caesar": [
            "Have you noticed any patterns in the text? Try shifting each letter...",
            "The Romans used this cipher thousands of years ago. Think about letter rotation.",
            "What happens when you shift 'A' by 3? Now try that with the whole message.",
            "The key might be a small number between 1 and 25. Experiment!"
        ],
        "base64": [
            "Look at the characters - do you see any '=' padding at the end?",
            "This encoding uses A-Z, a-z, 0-9, and two special characters.",
            "It's not encryption, it's encoding. The data is just transformed, not hidden.",
            "Try an online decoder or use: echo 'text' | base64 -d"
        ],
        "xor": [
            "XOR has a special property: A XOR B XOR B = A. Think about what that means.",
            "If you XOR with the same key twice, you get back the original!",
            "Try different single-byte keys (0-255) and look for readable output.",
            "The flag format usually starts with 'FLAG{' - can you use that to find the key?"
        ],
        "general": [
            "What type of encoding or cipher might this be?",
            "Look for patterns - repeated characters, special symbols, or known formats.",
            "Sometimes the hint is in how the data looks. Base64? Hex? Binary?",
            "Try identifying the cipher first before attempting to break it."
        ]
    },
    "web": {
        "sql_injection": [
            "What happens when you add a single quote ' to the input?",
            "Think about how the query might be constructed. Can you close it and add your own logic?",
            "Try: ' OR '1'='1 - what does this do to the SQL query?",
            "UNION attacks let you retrieve data from other tables. What's the column count?"
        ],
        "xss": [
            "Can you inject HTML tags? Try <b>test</b> first.",
            "If HTML works, what about <script> tags?",
            "Some filters can be bypassed with encoding or alternative event handlers.",
            "Try: <img src=x onerror=alert(1)> if script tags are blocked."
        ],
        "general": [
            "Always check the page source - developers leave clues!",
            "What requests does the page make? Check the Network tab.",
            "Try manipulating parameters in the URL or form data.",
            "Error messages often reveal valuable information about the system."
        ]
    },
    "forensics": {
        "file_analysis": [
            "What does the 'file' command tell you about this file?",
            "Check the file header (magic bytes) - is it what the extension claims?",
            "Try running 'strings' on the file to find readable text.",
            "Could there be hidden data appended after the file content?"
        ],
        "steganography": [
            "Not everything hidden is encrypted - sometimes it's just tucked away.",
            "Check the file's metadata with exiftool or similar tools.",
            "For images, try tools like steghide, zsteg, or stegsolve.",
            "LSB (Least Significant Bit) is a common hiding technique in images."
        ],
        "memory": [
            "Memory dumps contain lots of readable strings - try grep!",
            "Look for process names, URLs, passwords, or flag-like patterns.",
            "Volatility is the go-to tool for memory forensics.",
            "Search for common flag formats: FLAG{, CTF{, flag{, etc."
        ],
        "general": [
            "Forensics is about finding what's hidden in plain sight.",
            "Always start with basic analysis: file type, strings, metadata.",
            "Think like a detective - what story does the evidence tell?",
            "Multiple tools often reveal different pieces of the puzzle."
        ]
    },
    "reversing": {
        "general": [
            "Have you tried running 'strings' on the binary?",
            "Disassemblers like Ghidra or IDA can help you understand the code.",
            "Look for interesting function names - they often hint at the logic.",
            "Debug the program step by step to understand what it's checking."
        ]
    },
    "network": {
        "general": [
            "Open the capture in Wireshark and look for interesting protocols.",
            "Filter by protocol type - HTTP traffic often contains useful data.",
            "Follow the TCP stream to see the full conversation.",
            "Look for credentials, flags, or encoded data in the packets."
        ]
    },
    "misc": {
        "general": [
            "Think outside the box - this could involve any technique!",
            "Start with the basics: What type of data are you looking at?",
            "Research is key - Google the format or technique if unsure.",
            "Sometimes the simplest approach is the right one."
        ]
    }
}

# Proactive tips for different challenge contexts
PROACTIVE_TIPS = {
    "stuck_long_time": [
        "Taking a break can help! Fresh eyes often spot what tired ones miss.",
        "Have you tried approaching this from a different angle?",
        "Sometimes the answer is simpler than you think. Go back to basics!",
        "Reading the challenge description again might reveal a hidden clue."
    ],
    "multiple_failures": [
        "Every attempt teaches you something. What have you learned so far?",
        "Don't give up! The best hackers failed many times before succeeding.",
        "Try writing down what you've tried - patterns often emerge.",
        "Consider what the challenge category tells you about the approach."
    ],
    "first_challenge": [
        "Welcome! Take your time to understand the challenge before diving in.",
        "Start by reading the description carefully - hints are often hidden there.",
        "Don't be afraid to use the built-in hints if you get stuck!",
        "The learning journey matters more than the points."
    ],
    "encouragement": [
        "You're making progress! Keep going!",
        "Every challenge solved makes you a better security researcher.",
        "The fact that you're trying is what matters most.",
        "You've got this! Trust your instincts."
    ]
}


class AIService:
    def __init__(self, db: Session = None):
        self.db = db
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.models = settings.OLLAMA_MODELS

    async def _call_ollama(self, model: str, prompt: str, system_prompt: str = None) -> str:
        """Make a call to Ollama API"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }

                if system_prompt:
                    payload["system"] = system_prompt

                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json=payload,
                    timeout=120.0
                )

                if response.status_code == 200:
                    return response.json().get("response", "")
                else:
                    return f"Error: {response.status_code}"

        except Exception as e:
            return f"Error calling Ollama: {str(e)}"

    def start_challenge_generation_task(
        self,
        category: str,
        difficulty: str,
        topic: str,
        learning_objectives: List[str],
        user_skill_level: str,
        created_by: int
    ) -> str:
        """Start a background task for challenge generation"""
        task_id = str(uuid.uuid4())

        # In a real implementation, this would start a Celery task
        # For now, we'll return a task ID and simulate the process

        # Store task info (in a real app, this would be in Redis or database)
        self._store_task_info(task_id, {
            "status": "started",
            "category": category,
            "difficulty": difficulty,
            "topic": topic,
            "learning_objectives": learning_objectives,
            "user_skill_level": user_skill_level,
            "created_by": created_by,
            "created_at": datetime.now().isoformat()
        })

        return task_id

    def get_generation_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a challenge generation task"""
        # In a real implementation, this would check Celery task status
        # For now, simulate different statuses

        task_info = self._get_task_info(task_id)
        if not task_info:
            return None

        # Simulate task progression
        return {
            "task_id": task_id,
            "status": "completed",  # could be: started, processing, completed, failed
            "progress": 100,
            "result": {
                "challenge_id": 123,
                "title": "AI Generated Challenge",
                "description": "This is an AI-generated challenge for testing purposes."
            }
        }

    async def generate_personalized_hint(
        self,
        user_id: int,
        challenge_id: int,
        user_progress: Dict[str, Any],
        hint_level: int = 1
    ) -> Optional[str]:
        """Generate a personalized hint based on user's progress"""
        if not self.db:
            return "Database connection not available"

        # Get challenge details
        from app.services.challenge_service import ChallengeService
        challenge_service = ChallengeService(self.db)
        challenge = challenge_service.get_challenge_by_id(challenge_id)

        if not challenge:
            return None

        # Get user's previous attempts
        attempts = challenge_service.get_user_attempts(user_id, challenge_id)

        system_prompt = """You are an expert cybersecurity instructor providing hints for CTF challenges.
        Provide helpful hints that guide learning without giving away the solution directly.
        Tailor your hint to the user's skill level and previous attempts."""

        prompt = f"""
        Challenge: {challenge.title}
        Category: {challenge.category.name if challenge.category else 'Unknown'}
        Difficulty: {challenge.difficulty.value}
        Description: {challenge.description}

        User's previous attempts: {len(attempts)}
        Hint level requested: {hint_level}
        User progress: {json.dumps(user_progress)}

        Provide a hint that helps the user progress without giving away the solution.
        Make it educational and encouraging.
        """

        hint = await self._call_ollama("llama3", prompt, system_prompt)
        return hint if hint and not hint.startswith("Error") else None

    async def generate_feedback(
        self,
        user_id: int,
        challenge_id: int,
        user_attempt: str,
        is_correct: bool
    ) -> str:
        """Generate feedback on user's attempt"""
        if not self.db:
            return "Database connection not available"

        system_prompt = """You are an expert cybersecurity instructor providing feedback on CTF challenge attempts.
        Provide constructive feedback that helps users learn from their attempts."""

        prompt = f"""
        User's attempt was {'correct' if is_correct else 'incorrect'}.
        Attempt details: {user_attempt}

        Provide constructive feedback that:
        1. Acknowledges their effort
        2. Explains what they did well (if correct) or what went wrong (if incorrect)
        3. Suggests next steps for learning
        4. Encourages continued practice

        Keep the feedback encouraging and educational.
        """

        feedback = await self._call_ollama("llama3", prompt, system_prompt)
        return feedback if feedback and not feedback.startswith("Error") else "Great effort! Keep practicing."

    async def assess_user_skills(self, user_id: int) -> Dict[str, Any]:
        """Perform AI-based skill assessment for a user"""
        if not self.db:
            return {"error": "Database connection not available"}

        # Get user's challenge attempts and performance
        from app.services.analytics_service import AnalyticsService
        analytics_service = AnalyticsService(self.db)
        analytics = analytics_service.get_user_analytics(user_id)

        if not analytics:
            return {"assessment": "insufficient_data"}

        # Analyze performance patterns
        assessment = {
            "overall_skill_level": analytics.current_skill_level,
            "strengths": [],
            "weaknesses": [],
            "recommended_focus": [],
            "confidence_score": 0.75  # Placeholder
        }

        # This would use more sophisticated AI analysis in a real implementation
        if analytics.solve_rate > 0.8:
            assessment["strengths"].append("Problem solving")
        if analytics.solve_rate < 0.3:
            assessment["weaknesses"].append("Challenge completion")

        assessment["recommended_focus"] = ["Web security", "Cryptography"]

        return assessment

    async def recommend_difficulty_adjustment(
        self,
        user_id: int,
        challenge_id: int,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recommend difficulty adjustments based on performance"""
        time_spent = performance_data.get("time_spent", 0)
        hints_used = performance_data.get("hints_used", 0)
        attempts_count = performance_data.get("attempts_count", 1)

        recommendations = {
            "current_difficulty": "appropriate",
            "suggested_action": "continue",
            "reasoning": "Performance within expected range"
        }

        # Simple heuristic-based recommendations
        if time_spent > 3600 and hints_used > 3:  # More than 1 hour and many hints
            recommendations["current_difficulty"] = "too_hard"
            recommendations["suggested_action"] = "provide_easier_challenges"
            recommendations["reasoning"] = "User struggling with current difficulty level"
        elif time_spent < 300 and hints_used == 0:  # Less than 5 minutes, no hints
            recommendations["current_difficulty"] = "too_easy"
            recommendations["suggested_action"] = "provide_harder_challenges"
            recommendations["reasoning"] = "User completing challenges too quickly"

        return recommendations

    async def generate_learning_path(self, user_id: int, target_skill: str = "intermediate") -> Dict[str, Any]:
        """Generate a personalized learning path"""
        if not self.db:
            return {"error": "Database connection not available"}

        # Get user's current progress
        from app.services.analytics_service import AnalyticsService
        analytics_service = AnalyticsService(self.db)
        progress = analytics_service.get_user_progress(user_id)

        # Generate learning path based on current progress and target
        learning_path = {
            "target_skill_level": target_skill,
            "estimated_duration": "8-12 weeks",
            "phases": [
                {
                    "phase": 1,
                    "title": "Foundation Building",
                    "duration": "2-3 weeks",
                    "topics": ["Basic networking", "Linux fundamentals", "Web technologies"],
                    "challenges": []
                },
                {
                    "phase": 2,
                    "title": "Security Basics",
                    "duration": "3-4 weeks",
                    "topics": ["Common vulnerabilities", "Basic cryptography", "Security tools"],
                    "challenges": []
                },
                {
                    "phase": 3,
                    "title": "Practical Application",
                    "duration": "3-5 weeks",
                    "topics": ["Web application security", "Network security", "Incident response"],
                    "challenges": []
                }
            ]
        }

        return learning_path

    def get_models_status(self) -> Dict[str, Any]:
        """Get status of available AI models"""
        # This would check if Ollama models are available
        return {
            "ollama_url": self.ollama_base_url,
            "available_models": self.models,
            "status": "healthy",  # This would be checked dynamically
            "last_checked": datetime.now().isoformat()
        }

    def _store_task_info(self, task_id: str, info: Dict[str, Any]):
        """Store task information (placeholder for Redis/database)"""
        # In a real implementation, this would store in Redis or database
        pass

    def _get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task information (placeholder for Redis/database)"""
        # In a real implementation, this would retrieve from Redis or database
        return {"exists": True}  # Placeholder

    def get_smart_hint(self, category: str, challenge_title: str, hint_level: int = 1) -> str:
        """Get a smart hint based on challenge category and type"""
        category_lower = category.lower() if category else "misc"
        title_lower = challenge_title.lower() if challenge_title else ""

        # Determine subcategory based on title keywords
        subcategory = "general"
        if "caesar" in title_lower:
            subcategory = "caesar"
        elif "base64" in title_lower:
            subcategory = "base64"
        elif "xor" in title_lower:
            subcategory = "xor"
        elif "sql" in title_lower:
            subcategory = "sql_injection"
        elif "xss" in title_lower or "script" in title_lower:
            subcategory = "xss"
        elif "steg" in title_lower or "hidden" in title_lower:
            subcategory = "steganography"
        elif "memory" in title_lower or "dump" in title_lower:
            subcategory = "memory"
        elif "file" in title_lower or "metadata" in title_lower:
            subcategory = "file_analysis"

        # Get hints for this category
        category_hints = HINT_TEMPLATES.get(category_lower, HINT_TEMPLATES.get("misc", {}))
        hints = category_hints.get(subcategory, category_hints.get("general", []))

        if not hints:
            hints = HINT_TEMPLATES["misc"]["general"]

        # Return hint based on level (cycling through available hints)
        hint_index = (hint_level - 1) % len(hints)
        return hints[hint_index]

    def get_proactive_tip(self, context: str = "encouragement") -> str:
        """Get a proactive tip based on context"""
        tips = PROACTIVE_TIPS.get(context, PROACTIVE_TIPS["encouragement"])
        return random.choice(tips)

    async def smart_chatbot_response(
        self,
        message: str,
        challenge_id: Optional[int] = None,
        user_skill_level: str = "beginner",
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate a smart chatbot response with fallback when Ollama unavailable"""
        message_lower = message.lower()

        # Get challenge context if available
        challenge = None
        category_name = "general"
        if challenge_id and self.db:
            from app.services.challenge_service import ChallengeService
            challenge_service = ChallengeService(self.db)
            challenge = challenge_service.get_challenge_by_id(challenge_id)
            if challenge and challenge.category:
                category_name = challenge.category.name.lower()

        # Greetings
        if any(word in message_lower for word in ["hello", "hi", "hey", "howdy", "greetings", "sup", "good morning", "good afternoon", "good evening"]):
            greetings = [
                "Hey! 👋 Good to see you. Ask me anything — hints, concept explanations, tool recommendations, or just a chat about cybersecurity.",
                "Hi there! 😊 I'm your CTF learning assistant. What are you working on today?",
                "Hello! Ready to hack some challenges? 🚀 Tell me what you need help with.",
                "Hey! What's on your mind? I can explain concepts, suggest tools, or give you a nudge in the right direction.",
            ]
            return {
                "response": random.choice(greetings),
                "type": "greeting",
                "is_ai_generated": False
            }

        # How are you / small talk
        if any(phrase in message_lower for phrase in ["how are you", "how r u", "how's it going", "you okay", "are you good", "what's up", "whats up", "wassup"]):
            responses = [
                "I'm doing great, thanks for asking! 😄 Running on pure logic and caffeine-free code. How are YOU doing? Got a challenge you're stuck on?",
                "All good on my end — no bugs today (that I know of). What about you? Need help with anything?",
                "Fully operational! 🤖 What can I help you with today?",
            ]
            return {
                "response": random.choice(responses),
                "type": "greeting",
                "is_ai_generated": False
            }

        # Thank you
        if any(word in message_lower for word in ["thank", "thanks", "thx", "cheers", "appreciate"]):
            responses = [
                "You're welcome! 🎉 Keep at it — you're doing great!",
                "Happy to help! 😊 That's what I'm here for. Good luck with the challenge!",
                "Anytime! 🚀 Every step forward counts. Let me know if you need anything else.",
            ]
            return {
                "response": random.choice(responses),
                "type": "encouragement",
                "is_ai_generated": False
            }

        # Check for hint requests
        if any(word in message_lower for word in ["hint", "help", "stuck", "clue", "tip"]):
            if challenge:
                hint = self.get_smart_hint(category_name, challenge.title, 1)
                return {
                    "response": f"💡 Here's a hint for you:\n\n{hint}\n\nRemember, the best learning comes from figuring things out yourself! Would you like another hint?",
                    "type": "hint",
                    "is_ai_generated": False
                }
            else:
                return {
                    "response": "I'd love to help! Which challenge are you working on? Tell me more about what you're trying to solve.",
                    "type": "clarification",
                    "is_ai_generated": False
                }

        # Check for concept explanations
        if any(word in message_lower for word in ["what is", "explain", "how does", "tell me about", "teach me", "learn"]):
            response = self._explain_concept(message_lower)
            return {
                "response": response,
                "type": "explanation",
                "is_ai_generated": False
            }

        # Check for tool recommendations
        if any(word in message_lower for word in ["tool", "software", "program", "what should i use", "recommend"]):
            response = self._recommend_tools(message_lower, category_name)
            return {
                "response": response,
                "type": "tools",
                "is_ai_generated": False
            }

        # Check for encouragement needs
        if any(word in message_lower for word in ["can't", "cannot", "impossible", "give up", "too hard", "no idea", "lost", "confused"]):
            tip = self.get_proactive_tip("encouragement")
            return {
                "response": f"🌟 {tip}\n\nEvery expert was once a beginner. Would you like me to give you a hint to help you progress?",
                "type": "encouragement",
                "is_ai_generated": False
            }

        # Try Ollama if available
        try:
            ollama_available = await self._check_ollama_status()
            if ollama_available:
                context = f"User skill level: {user_skill_level}\n"
                context += f"User message: {message}\n"

                if challenge:
                    context += f"\nCurrent challenge: {challenge.title}\n"
                    context += f"Category: {category_name}\n"
                    context += f"Difficulty: {challenge.difficulty}\n"

                system_prompt = """You are a friendly CTF mentor helping students learn cybersecurity.

RULES:
1. NEVER give the flag or direct solution
2. Guide with questions and hints
3. Explain concepts when asked
4. Keep responses short (2-3 sentences)
5. Be encouraging and supportive
6. Use simple language for beginners

Your goal is to help them learn, not solve it for them."""

                response = await self._call_ollama("llama3", context, system_prompt)
                if response and not response.startswith("Error"):
                    return {
                        "response": response,
                        "type": "ai_response",
                        "is_ai_generated": True
                    }
        except Exception:
            pass

        # Generic fallback — acknowledge the message and offer help
        if challenge:
            hint = self.get_smart_hint(category_name, challenge.title, 1)
            return {
                "response": f"I'm here to help you with '{challenge.title}'! 🎯\n\nHere's something to think about:\n{hint}\n\nWhat have you tried so far?",
                "type": "guidance",
                "is_ai_generated": False
            }

        generic_responses = [
            "Interesting! I'm not sure I fully caught that — could you rephrase? I can help with hints, concept explanations, tool recommendations, or just general CTF guidance. 😊",
            "Got it! To give you the best help, could you be more specific? Are you stuck on a challenge, want to learn a concept, or looking for tool recommendations?",
            "I want to help! Ask me about a specific concept (like SQL injection or Base64), request a hint, or ask what tools to use for a category. 🔐",
        ]
        return {
            "response": random.choice(generic_responses),
            "type": "clarification",
            "is_ai_generated": False
        }

    async def _check_ollama_status(self) -> bool:
        """Check if Ollama is available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_base_url}/api/tags", timeout=2.0)
                return response.status_code == 200
        except Exception:
            return False

    def _explain_concept(self, message: str) -> str:
        """Explain cybersecurity concepts"""
        concepts = {
            "caesar": "The Caesar cipher shifts each letter by a fixed number. For example, with a shift of 3, 'A' becomes 'D'. It's one of the oldest encryption methods! Try shifting the letters and look for readable text.",
            "base64": "Base64 is an encoding (not encryption!) that converts binary data to text using 64 characters. Look for the telltale '=' padding at the end. You can decode it with online tools or command line.",
            "xor": "XOR (exclusive or) is a bitwise operation. The magic is: if A XOR B = C, then C XOR B = A. Single-byte XOR can be broken by trying all 256 possible keys!",
            "sql injection": "SQL injection happens when user input is inserted directly into database queries. Try adding special characters like ' or \" to see if you can break the query structure.",
            "xss": "Cross-Site Scripting (XSS) lets attackers inject scripts into web pages. If you can inject HTML, you might be able to inject JavaScript too!",
            "steganography": "Steganography hides data within other files (like images). Tools like steghide, exiftool, and strings can reveal hidden content.",
            "forensics": "Digital forensics is about finding evidence in files and data. Start with basic tools: 'file' to check type, 'strings' to find text, 'xxd' for hex dumps.",
            "buffer overflow": "Buffer overflows happen when a program writes beyond allocated memory. This can overwrite important data like return addresses!",
            "hash": "Hashing creates a fixed-size fingerprint of data. Common hashes: MD5 (32 hex chars), SHA1 (40 hex chars), SHA256 (64 hex chars). They're one-way functions!",
        }

        for keyword, explanation in concepts.items():
            if keyword in message:
                return f"📚 **{keyword.title()}**\n\n{explanation}"

        return "That's a great topic to explore! Try searching for it in the challenge categories, or ask me about specific concepts like Caesar cipher, SQL injection, or steganography."

    def _recommend_tools(self, message: str, category: str) -> str:
        """Recommend tools based on category"""
        tool_recommendations = {
            "cryptography": "🔧 **Crypto Tools:**\n• CyberChef - Swiss army knife for encoding/decoding\n• hashcat - Password cracking\n• John the Ripper - Password cracker\n• Python - For custom scripts",
            "web": "🔧 **Web Tools:**\n• Burp Suite - Web proxy and scanner\n• Browser DevTools - Network & source inspection\n• SQLMap - SQL injection testing\n• curl - HTTP requests",
            "forensics": "🔧 **Forensics Tools:**\n• strings - Find readable text\n• file - Identify file types\n• exiftool - Metadata analysis\n• binwalk - Firmware analysis\n• Volatility - Memory forensics",
            "steganography": "🔧 **Stego Tools:**\n• steghide - Hide/extract data\n• zsteg - PNG/BMP analysis\n• stegsolve - Image layer analysis\n• exiftool - Metadata extraction",
            "reversing": "🔧 **RE Tools:**\n• Ghidra - Free disassembler\n• IDA Free - Disassembler\n• gdb - Debugger\n• strings - Find text in binaries",
            "network": "🔧 **Network Tools:**\n• Wireshark - Packet analysis\n• tcpdump - Packet capture\n• nmap - Network scanning\n• netcat - Network Swiss army knife"
        }

        return tool_recommendations.get(category, tool_recommendations.get("forensics", "Try CyberChef for encoding/decoding tasks, and the 'strings' command for finding hidden text!"))