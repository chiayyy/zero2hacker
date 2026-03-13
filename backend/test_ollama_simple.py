"""
Simple Ollama connection test (ASCII only for Windows console)
"""
import asyncio
import httpx
from app.services.ai_service import AIService


async def test_ollama():
    print("\n" + "="*60)
    print("TESTING OLLAMA CONNECTION")
    print("="*60)

    try:
        async with httpx.AsyncClient() as client:
            # Test connection
            print("\n[TEST 1] Checking Ollama service...")
            response = await client.get("http://localhost:11434/api/tags")

            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"[OK] Ollama is running")
                print(f"[OK] Found {len(models)} models:")
                for model in models:
                    size_gb = model['size'] / 1e9
                    print(f"     - {model['name']} ({size_gb:.1f} GB)")
            else:
                print(f"[FAIL] Ollama returned status {response.status_code}")
                return False

            # Test generation
            print("\n[TEST 2] Testing AI generation...")
            payload = {
                "model": "llama3",
                "prompt": "Explain what SQL injection is in one sentence.",
                "stream": False
            }

            response = await client.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=60.0
            )

            if response.status_code == 200:
                result = response.json()
                generated = result.get("response", "")
                print(f"[OK] Generation successful!")
                print(f"Response: {generated[:200]}...")
            else:
                print(f"[FAIL] Generation failed: {response.status_code}")
                return False

            return True

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False


async def test_ai_service_class():
    print("\n" + "="*60)
    print("TESTING AI SERVICE CLASS")
    print("="*60)

    try:
        ai_service = AIService()

        print("\n[TEST 3] Testing AI Service configuration...")
        print(f"Ollama URL: {ai_service.ollama_base_url}")
        print(f"Models: {ai_service.models}")

        print("\n[TEST 4] Generating educational CTF hint...")
        system_prompt = """You are a cybersecurity instructor.
        Provide helpful hints that guide learning without revealing solutions."""

        prompt = """A beginner is working on their first SQL injection challenge.
        They keep trying to use XSS payloads instead.
        Give a 1-2 sentence hint to guide them toward SQL injection without revealing the solution."""

        hint = await ai_service._call_ollama("llama3", prompt, system_prompt)

        if hint and not hint.startswith("Error"):
            print(f"[OK] Hint generated!")
            print(f"\nGenerated Hint:\n{hint}\n")
            return True
        else:
            print(f"[FAIL] Hint generation failed: {hint}")
            return False

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("\nZERO2HACKER CTF - OLLAMA INTEGRATION TEST")
    print("="*60)

    # Run tests
    test1 = await test_ollama()
    if not test1:
        print("\n[FAIL] Ollama connection test failed")
        return

    test2 = await test_ai_service_class()
    if not test2:
        print("\n[FAIL] AI Service test failed")
        return

    print("\n" + "="*60)
    print("[SUCCESS] ALL TESTS PASSED!")
    print("Ollama is ready for API integration")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
