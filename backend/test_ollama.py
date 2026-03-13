"""
Test script to verify Ollama connection and AI service functionality
"""
import asyncio
import httpx
from app.services.ai_service import AIService


async def test_ollama_connection():
    """Test basic Ollama API connection"""
    print("=" * 60)
    print("TESTING OLLAMA CONNECTION")
    print("=" * 60)

    try:
        async with httpx.AsyncClient() as client:
            # Test 1: Check Ollama is running
            print("\n1. Checking Ollama service...")
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"   ✓ Ollama is running")
                print(f"   ✓ Available models: {len(models)}")
                for model in models:
                    print(f"     - {model['name']} ({model['size'] / 1e9:.1f} GB)")
            else:
                print(f"   ✗ Ollama returned status {response.status_code}")
                return False

            # Test 2: Generate simple response
            print("\n2. Testing AI generation...")
            payload = {
                "model": "llama3",
                "prompt": "Say 'Hello from Ollama!' and nothing else.",
                "stream": False
            }

            response = await client.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "")
                print(f"   ✓ Generation successful")
                print(f"   Response: {generated_text[:100]}")
            else:
                print(f"   ✗ Generation failed: {response.status_code}")
                return False

            print("\n✓ All Ollama tests passed!")
            return True

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


async def test_ai_service():
    """Test AIService class"""
    print("\n" + "=" * 60)
    print("TESTING AI SERVICE CLASS")
    print("=" * 60)

    try:
        ai_service = AIService()

        # Test 1: Check configuration
        print("\n1. Checking AI Service configuration...")
        print(f"   Ollama URL: {ai_service.ollama_base_url}")
        print(f"   Models: {ai_service.models}")

        # Test 2: Generate personalized hint (without database)
        print("\n2. Testing hint generation...")
        system_prompt = "You are a cybersecurity instructor. Provide a brief hint."
        prompt = "User is stuck on a SQL injection challenge. Give a gentle hint without revealing the solution."

        hint = await ai_service._call_ollama("llama3", prompt, system_prompt)

        if hint and not hint.startswith("Error"):
            print(f"   ✓ Hint generated successfully")
            print(f"   Hint preview: {hint[:150]}...")
        else:
            print(f"   ✗ Hint generation failed: {hint}")
            return False

        # Test 3: Test model status
        print("\n3. Checking model status...")
        status = ai_service.get_models_status()
        print(f"   Ollama URL: {status['ollama_url']}")
        print(f"   Available models: {status['available_models']}")
        print(f"   Status: {status['status']}")

        print("\n✓ All AI Service tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_educational_hint():
    """Test generating an educational CTF hint"""
    print("\n" + "=" * 60)
    print("TESTING EDUCATIONAL HINT GENERATION")
    print("=" * 60)

    ai_service = AIService()

    # Simulate a real CTF scenario
    system_prompt = """You are an expert cybersecurity instructor providing hints for CTF challenges.
    Your hints should:
    - Guide learning without giving away the solution
    - Be educational and explain concepts
    - Encourage critical thinking
    - Be appropriate for the difficulty level
    """

    challenge_context = """
    Challenge: Caesar's Secret
    Category: Cryptography
    Difficulty: Beginner
    Description: You've intercepted an encrypted message: "Khoor Zruog"
    The user has tried: Base64 decoding (wrong approach)
    Hint level: 1 (first hint)
    """

    prompt = f"""{challenge_context}

    Provide the first hint for this challenge. Remember:
    - Don't reveal it's a Caesar cipher
    - Point them toward classical cryptography
    - Keep it under 2 sentences
    - Be encouraging
    """

    print("\nGenerating educational hint...")
    hint = await ai_service._call_ollama("llama3", prompt, system_prompt)

    print(f"\nGenerated Hint:")
    print(f"└─ {hint}")

    return hint


async def main():
    """Run all tests"""
    print("\nZERO2HACKER CTF - OLLAMA INTEGRATION TEST")
    print("=" * 60)

    # Run tests
    test1 = await test_ollama_connection()
    if not test1:
        print("\n❌ Ollama connection failed. Please check if Ollama is running.")
        return

    test2 = await test_ai_service()
    if not test2:
        print("\n❌ AI Service test failed.")
        return

    await test_educational_hint()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - Ready for API integration!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
