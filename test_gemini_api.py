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
        # 429 Rate Limit/Resource Exhausted もしくは 500 Internal Error の場合は CI をブロックしないよう正常終了（スキップ扱い）にする
        is_skippable = (
            "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or
            "500" in error_msg or "INTERNAL" in error_msg
        )
        if is_skippable:
            print(f"Gemini API temporary error (e.g. rate limit, credits depleted, or server internal error): {e}")
            print("Skipping API test and exiting with status 0 to avoid blocking CI.")
            sys.exit(0)
        else:
            print(f"Gemini API test failed with unexpected error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
