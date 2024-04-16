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

def create_external_embed(title, description, url):
    return models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(
            title=title,
            description=description,
            uri=url
        )
    )

def format_message_with_link(title, url, introduction, content):
    formatted_content = content.replace("\n", "").replace("。", "。\n")
    return client_utils.TextBuilder().text(f"{introduction}\n\n").link(title, url).text(f"\n{formatted_content}")

def authenticate_and_post(bs_client, username, password, content, embed):
    bs_client.login(username, password)
    bs_client.send_post(content, embed=embed)
