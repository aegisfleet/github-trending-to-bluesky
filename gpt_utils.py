import google.generativeai as genai
import time
import gemini_model

def remove_last_sentence(text):
    sentences = text.split('。')
    if sentences[-1] == '':
        sentences.pop()
    if sentences:
        sentences.pop()
    if sentences:
        result = '。'.join(sentences) + '。'
        return result
    return ""

def get_description(api_key, text, limit_size, max_retries=3):
    genai.configure(api_key=f"{api_key}")
    model = genai.GenerativeModel(gemini_model.MODEL_NAME)

    def attempt_request(retry_count):
        response_text = ""
        try:
            prompt = text.replace("[limit_size]", str(limit_size - (retry_count * 20)))
            response = model.generate_content(f"{prompt}")
            response_text = response.text
            if not response_text or response_text.strip() == "":
                raise ValueError(
                    f"レスポンスが空です。"
                )
            if len(response_text) > limit_size:
                raise ValueError(
                    f"レスポンスの文字数が{limit_size}文字を超えています。"
                )
            return response_text
        except ValueError as e:
            print(
                f"リトライ回数: {retry_count}\n{e}\n{response_text}"
            )
            time.sleep(3)
        except Exception as e:
            print(
                f"予期しないエラーが発生しました。リトライ回数: {retry_count}\n"
                f"エラータイプ: {type(e).__name__}\nエラーメッセージ: {e}"
            )
            time.sleep(30)

        if retry_count < max_retries:
            return attempt_request(retry_count + 1)
        else:
            print("最大リトライ回数に達しました。")
            return remove_last_sentence(response_text)

    return attempt_request(0)
