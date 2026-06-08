import argparse
import os
from gemini_model import generate_text_with_gemini

def main():
    parser = argparse.ArgumentParser(description="Test Gemini API")
    parser.add_argument("api_key", nargs="?", default=None, help="Gemini API key")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")

    if not api_key or api_key.strip() == "":
        print("Gemini API key is not configured. Skipping API test.")
        exit(0)

    prompt = "フレンドリーなロボットについての短い物語を書いてください。日本語で回答してください。"
    generated_text = generate_text_with_gemini(api_key=api_key, prompt_text=prompt)

    if generated_text:
        print("Gemini API test successful!")
        print("Generated text:")
        print(generated_text)
        exit(0)
    else:
        print("Gemini API test failed.")
        exit(1)

if __name__ == "__main__":
    main()
