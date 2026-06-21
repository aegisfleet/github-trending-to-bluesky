import argparse
import os
import sys
from gemini_model import generate_text_with_gemini

def main():
    parser = argparse.ArgumentParser(description="Test Gemini API")
    parser.add_argument("api_key", nargs="?", default=None, help="Gemini API key")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")

    if not api_key or api_key.strip() == "":
        print("Gemini API key is not configured. Skipping API test.")
        sys.exit(0)

    prompt = "フレンドリーなロボットについての短い物語を書いてください。日本語で回答してください。"
    
    try:
        generated_text = generate_text_with_gemini(api_key=api_key, prompt_text=prompt)
        print("Gemini API test successful!")
        print("Generated text:")
        print(generated_text)
        sys.exit(0)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            print(f"Gemini API rate limit or resource exhausted (e.g. credits depleted): {e}")
            print("Skipping API test and exiting with status 0 to avoid blocking CI.")
            sys.exit(0)
        else:
            print(f"Gemini API test failed with unexpected error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
