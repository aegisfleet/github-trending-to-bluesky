MODEL_NAME = 'gemma-4-31b-it'

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
    Generates text using the Gemini API.

    Args:
        api_key: The Gemini API key.
        prompt_text: The prompt to send to the model.

    Returns:
        The generated text, or None if an error occurred.
    """
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt_text,
        )
        return extract_answer_text(response)
    except Exception as e:
        print(f"Error generating text with Gemini: {e}")
        return None
