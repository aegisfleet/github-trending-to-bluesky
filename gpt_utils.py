import google.generativeai as genai
import time

def remove_last_sentence(text):
    sentences = text.split('。')
    if sentences[-1] == '':
        sentences.pop()
    if sentences:
        sentences.pop()
    result = '。'.join(sentences) + '。'
    return result

def get_description(api_key, text, limit_size, max_retries=3):
    genai.configure(api_key=f"{api_key}")
    model = genai.GenerativeModel('gemini-1.5-flash-002')

    def attempt_request(retry_count):
        response_text = ""
        try:
            prompt = text.replace("[limit_size]", str(limit_size - (retry_count * 20)))
            response = model.generate_content(f"{prompt}")
            response_text = response.text
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
