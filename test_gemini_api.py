import argparse
from gemini_model import generate_text_with_gemini

def main():
    parser = argparse.ArgumentParser(description="Test Gemini API")
    parser.add_argument("api_key", help="Gemini API key")
    args = parser.parse_args()

    prompt = "フレンドリーなロボットについての短い物語を書いてください。日本語で回答してください。"
    generated_text = generate_text_with_gemini(api_key=args.api_key, prompt_text=prompt)

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
