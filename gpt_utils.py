import google.generativeai as genai
import time

def get_description(api_key, text, limit_size, max_retries=3):
    genai.configure(api_key=f"{api_key}")
    model = genai.GenerativeModel('gemini-1.5-flash')

    def attempt_request(retry_count):
        try:
            response = model.generate_content(f"{text}")
            if len(response.text) > limit_size:
                raise ValueError(
                    f"レスポンスの文字数が{limit_size}文字を超えています。"
                )
            return response.text
        except ValueError as e:
            print(
                f"リトライ回数: {retry_count}\n{e}\n{response.text}"
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
            raise Exception("最大リトライ回数に達しました。")

    return attempt_request(0)
