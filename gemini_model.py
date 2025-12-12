MODEL_NAME = 'gemma-3-27b-it'

import google.generativeai as genai

def generate_text_with_gemini(api_key: str, prompt_text: str) -> str | None:
    """
    Generates text using the Gemini API.

    Args:
        api_key: The Gemini API key.
        prompt_text: The prompt to send to the model.

    Returns:
        The generated text, or None if an error occurred.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        print(f"Error generating text with Gemini: {e}")
        return None
