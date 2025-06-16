import os
import sys
from gemini_model import generate_text_with_gemini

def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        sys.exit(1)

    prompt = "Write a short story about a friendly robot."
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
