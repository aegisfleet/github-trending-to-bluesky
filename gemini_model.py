MODEL_NAME = 'gemma-4-31b-it'

import time
from google import genai


def extract_answer_text(response):
    """レスポンスから thinking パートを除外し、最終回答テキストのみを返す"""
    parts = response.candidates[0].content.parts
    answer_texts = []
    for part in parts:
        if getattr(part, 'thought', False):
            continue
        if part.text:
            answer_texts.append(part.text)
    return "".join(answer_texts)


def generate_text_with_gemini(api_key: str, prompt_text: str) -> str | None:
    """
    Generates text using the Gemini API with exponential backoff retry for rate limits.

    Args:
        api_key: The Gemini API key.
        prompt_text: The prompt to send to the model.

    Returns:
        The generated text, or None if an error occurred.
    """
    max_retries = 5
    initial_delay = 2.0
    backoff_factor = 2.0

    client = genai.Client(api_key=api_key)

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt_text,
            )
            return extract_answer_text(response)
        except Exception as e:
            error_msg = str(e)
            is_rate_limit = "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg
            
            # Check code attribute if it exists
            code = getattr(e, "code", None)
            if code == 429 or code == 8:
                is_rate_limit = True

            if is_rate_limit and attempt < max_retries - 1:
                delay = initial_delay * (backoff_factor ** attempt)
                print(f"Gemini API rate limit hit (429/RESOURCE_EXHAUSTED). Retrying in {delay:.1f} seconds (Attempt {attempt + 1}/{max_retries})...")
                time.sleep(delay)
            else:
                print(f"Error generating text with Gemini: {e}")
                return None
    return None
