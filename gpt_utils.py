import g4f
import time
from g4f.cookies import set_cookies
from g4f.errors import RateLimitError

def setup_cookies():
    set_cookies(".bing.com", {
        "_U": "cookie value"
    })

def get_description(gpt_client, text, max_retries=3):
    def attempt_request(retry_count):
        try:
            response = gpt_client.chat.completions.create(
                model="gpt-4-turbo",
                provider=g4f.Provider.Bing,
                messages=[
                    {"role": "user", "content": f"{text}"}
                ],
            )
            content = response.choices[0].message.content
            if len(content) > 250:
                raise ValueError(
                    "レスポンスの文字数が250文字を超えています。"
                )
            return content
        except RateLimitError:
            print(
                f"RateLimitErrorが発生しました。リトライ回数: {retry_count}"
            )
            time.sleep(30)
        except ValueError:
            print(
                f"ValueErrorが発生しました。レスポンスの文字数が250文字を超えています。"
                f"リトライ回数: {retry_count}\n{content}"
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
