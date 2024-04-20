import httpx
import requests
from bs4 import BeautifulSoup
from atproto import models, client_utils

def fetch_webpage_metadata(url):
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except Exception as error:
        print(f"リクエスト中にエラーが発生しました: {error}")
        return "", "", ""

    return parse_html_for_metadata(response.text)

def parse_html_for_metadata(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    title = soup.find("title").text if soup.find("title") else ""
    description = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    image = soup.find("meta", attrs={"property": "og:image"})

    description_content = description.get("content", "") if description else ""
    image_url = image.get("content", "") if image else ""

    return title, description_content, image_url

def authenticate(bs_client, username, password):
    bs_client.login(username, password)

def format_message_with_link(title, url, introduction, content):
    formatted_content = content.replace("\n", "").replace("。", "。\n")
    return client_utils.TextBuilder().text(f"{introduction}\n\n").link(title, url).text(f"\n{formatted_content}")

def create_external_embed(bs_client, title, description, url, img_url):
    trimmed_desc = description.replace("\n", "")[:200]
    img_data = httpx.get(img_url).content
    thumb_blob = bs_client.upload_blob(img_data).blob
    return models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(
            title=title,
            description=trimmed_desc,
            uri=url,
            thumb=thumb_blob
        )
    )

def post(bs_client, text, embed):
    bs_client.send_post(text, embed=embed)
