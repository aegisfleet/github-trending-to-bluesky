import io
import requests
import time
from atproto import models, client_utils
from atproto_client.exceptions import UnauthorizedError, NetworkError
from bs4 import BeautifulSoup, Tag
from PIL import Image

HTML_PARSER = "html.parser"

def fetch_webpage_metadata(url):
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
    except Exception as error:
        print(f"リクエスト中にエラーが発生しました: {error}")
        return "", "", ""

    return parse_html_for_metadata(response.text)

def parse_html_for_metadata(html_content):
    soup = BeautifulSoup(html_content, HTML_PARSER)

    title = soup.find("title")
    title_text = title.get_text() if title else ""

    description = soup.find("meta", attrs={"name": "description"}) or \
                  soup.find("meta", attrs={"property": "og:description"})
    image = soup.find("meta", attrs={"property": "og:image"})

    description_content = description["content"] if description and isinstance(description, Tag) else ""
    image_url = image["content"] if image and isinstance(image, Tag) else ""

    title_text = BeautifulSoup(title_text, HTML_PARSER).get_text()
    description_content = BeautifulSoup(description_content if isinstance(description_content, str) else "", HTML_PARSER).get_text()

    return title_text, description_content, image_url

def _resolve_pds_endpoint(handle):
    """ハンドルからPDSエンドポイントを解決する。
    1. DNS TXTレコード(_atproto.{handle})でDIDを取得
    2. plc.directoryでDIDドキュメントを取得しPDSエンドポイントを抽出
    """
    import dns.resolver
    try:
        # DNS TXTレコードからDIDを解決
        txt_name = f"_atproto.{handle}"
        print(f"DNS TXTレコードを確認: {txt_name}")
        answers = dns.resolver.resolve(txt_name, "TXT")
        did = None
        for rdata in answers:
            txt_value = rdata.strings[0].decode("utf-8")
            if txt_value.startswith("did="):
                did = txt_value[4:]
                break
        if not did:
            print("DNS TXTレコードからDIDを取得できなかった")
            return None
        print(f"DIDを解決した: {did}")
    except Exception as e:
        print(f"DNS解決に失敗した: {e}")
        # フォールバック: HTTPS経由でwell-knownからDIDを解決
        try:
            well_known_url = f"https://{handle}/.well-known/atproto-did"
            resp = requests.get(well_known_url, timeout=10)
            resp.raise_for_status()
            did = resp.text.strip()
            print(f"well-known経由でDIDを解決した: {did}")
        except Exception as e2:
            print(f"well-known経由のDID解決にも失敗した: {e2}")
            return None

    # plc.directoryでPDSエンドポイントを取得
    try:
        plc_url = f"https://plc.directory/{did}"
        print(f"PLC directoryに問い合わせ: {plc_url}")
        resp = requests.get(plc_url, timeout=10)
        resp.raise_for_status()
        did_doc = resp.json()
        services = did_doc.get("service", [])
        for svc in services:
            if svc.get("type") == "AtprotoPersonalDataServer":
                pds_url = svc.get("serviceEndpoint")
                print(f"PDSエンドポイントを取得した: {pds_url}")
                return pds_url
        print("DIDドキュメントにPDSエンドポイントが見つからなかった")
    except Exception as e:
        print(f"PLC directory of {did} に問い合わせ失敗: {e}")
    return None

def _try_login(client, username, password, retries=3, wait_time=5, label=""):
    """指定クライアントでログインを試行し、成功時にクライアントを返す。失敗時はNone。"""
    for attempt in range(retries):
        try:
            client.login(username, password)
            print(f"{label}認証に成功した")
            return client
        except (UnauthorizedError, NetworkError, Exception) as e:
            _log_auth_error(attempt, e, label)
            if attempt < retries - 1:
                time.sleep(wait_time)
    return None

def _log_auth_error(attempt, error, label=""):
    """認証エラーのログ出力。"""
    is_elb_error = "awselb" in str(error) or "403 Forbidden" in str(error)
    if is_elb_error:
        print(f"{label}試行 {attempt + 1}: ELB/インフラレベルのエラーを検出")
    else:
        print(f"{label}試行 {attempt + 1} 失敗: {error}")

def authenticate(bs_client, username, password, retries=3, wait_time=5):
    """認証を行い、認証済みクライアントを返す。
    bsky.socialに接続できない場合、PDS直接接続にフォールバックする。
    フォールバック時は新しいクライアントが返される。
    """
    # まずデフォルトエンドポイント(bsky.social)で試行
    result = _try_login(bs_client, username, password, retries, wait_time)
    if result:
        return result

    # デフォルトエンドポイントが全て失敗した場合、PDS直接接続を試行
    print("デフォルトエンドポイントへの接続に失敗した。PDS直接接続を試行する...")
    pds_url = _resolve_pds_endpoint(username)
    if pds_url:
        from atproto import Client as BSClient
        pds_client = BSClient(base_url=pds_url)
        result = _try_login(pds_client, username, password, retries, wait_time, label="PDS直接接続 ")
        if result:
            return result

    raise ConnectionError("全ての認証方法が失敗した。Blueskyのサービス状態を確認してください。")

def format_message(title, introduction, content):
    formatted_content = content.strip().replace("  ", "").replace("\n", "").replace("。", "。\n")
    return client_utils.TextBuilder().text(f"{introduction}\n\n{title}\n{formatted_content}")

def format_message_with_link(title, url, introduction, content):
    formatted_content = content.strip().replace("  ", "").replace("\n", "").replace("。", "。\n")
    return client_utils.TextBuilder().text(f"{introduction}\n\n")\
                                      .link(title, url)\
                                      .text(f"\n{formatted_content}")

def compress_image(image_bytes, max_size_kb=500, quality=85):
    img = Image.open(io.BytesIO(image_bytes))

    if img.mode in ['RGBA', 'P']:
        img = img.convert('RGB')

    while True:
        with io.BytesIO() as output:
            img.save(output, format="JPEG", quality=quality)
            compressed_bytes = output.getvalue()
            size_kb = len(compressed_bytes) / 1024
            if size_kb <= max_size_kb:
                return compressed_bytes

        if quality > 20:
            quality -= 5
        else:
            img = img.resize((img.width * 9 // 10, img.height * 9 // 10), 
                             resample=Image.Resampling.LANCZOS)

def _download_image(url, retries=3):
    for attempt in range(1, retries + 1):
        try:
            img_response = requests.get(url, timeout=30)
            img_response.raise_for_status()
            return img_response.content
        except requests.RequestException as e:
            print(f"画像データの取得に失敗しました: {e} リトライ回数: {attempt}")
            if attempt < retries:
                time.sleep(10)
            else:
                print("画像の取得に最終的に失敗しました。サムネイルなしで進めます。")
    return None

def _upload_thumbnail(bs_client, img_data, retries=3):
    compressed_img_data = compress_image(img_data)
    for attempt in range(1, retries + 1):
        try:
            return bs_client.upload_blob(compressed_img_data).blob
        except NetworkError as e:
            print(f"サムネイルのアップロードに失敗しました: {e} リトライ回数: {attempt}")
            if attempt < retries:
                time.sleep(10)
            else:
                print("サムネイルのアップロードに最終的に失敗しました。サムネイルなしで進めます。")
    return None

def create_external_embed(bs_client, title, description, url, img_url):
    trimmed_desc = description.replace("\n", "")[:200]
    img_data = _download_image(img_url) if img_url else None
    thumb_blob = _upload_thumbnail(bs_client, img_data) if img_data else None

    return models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(
            title=title,
            description=trimmed_desc,
            uri=url,
            thumb=thumb_blob
        )
    )

def post(bs_client, text, embed):
    retries = 3
    for attempt in range(1, retries + 1):
        try:
            bs_client.send_post(text, embed=embed)
            break
        except Exception as e:
            print(f"送信に失敗しました。リトライします... リトライ回数: {attempt}, エラー: {e}")
            time.sleep(3)
    else:
        print("リトライ上限に達しました。送信に失敗しました。")
