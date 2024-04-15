import requests
import sys
import g4f
from bs4 import BeautifulSoup
from g4f.client import Client as GPTClient
from g4f.cookies import set_cookies
from atproto import Client as BSClient, client_utils, models

def setup_cookies():
    set_cookies(".bing.com", {
        "_U": "cookie value"
    })

def print_usage_and_exit():
    print("使用法: python main.py <ユーザーハンドル> <パスワード>")
    sys.exit(1)

def get_link_card_info(url: str):
    title, description, image_url = '', '', ''
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except Exception as e:
        print(f"リクエスト中にエラーが発生しました: {e}")
        return title, description, image_url

    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find('title')
    description_meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
    image_meta = soup.find('meta', attrs={'property': 'og:image'})

    if title_tag:
        title = title_tag.text
    if description_meta:
        description = description_meta.get('content', '')
    if image_meta:
        image_url = image_meta.get('content', '')

    return title, description, image_url

def get_trending_repositories(url='https://github.com/trending', count=5):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    repo_elements = soup.find_all('h2', class_='h3 lh-condensed')[:count]

    repositories = []
    for repo_element in repo_elements:
        a_tag = repo_element.find('a')
        href = a_tag['href']
        name = a_tag.text.split('/')[-1].replace('\n', '').strip()
        full_url = f'https://github.com{href}'
        repositories.append((full_url, href, name))

    return repositories

def get_repository_description(gpt_client, repo_href, text):
    response = gpt_client.chat.completions.create(
        model="gpt-4-turbo",
        provider=g4f.Provider.Bing,
        messages=[{"role": "user", "content": f"{repo_href}リポジトリは誰がいつどこで使うものか250文字以下で3行にまとめて欲しい。\n回答は日本語で強調文字は使用せず簡素にする。\n以下にリポジトリのREADMEを記載する。\n\n{text}"}],
    )
    return response.choices[0].message.content

def get_readme_text(repo_href):
    readme_urls = [
        f"https://raw.githubusercontent.com{repo_href}/main/README.md",
        f"https://raw.githubusercontent.com{repo_href}/master/README.md"
    ]
    for url in readme_urls:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text[:300]
    return ''

def prepare_embed_external(title, description, url):
    return models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(
            title=title,
            description=description,
            uri=url
        )
    )

def prepare_text(repo_name, repo_url, message):
    message_with_breaks = message.replace('\n', '').replace('。', '。\n')
    return client_utils.TextBuilder().text('今日のGitHubトレンド\n\n').link(f'{repo_name}', f'{repo_url}').text('\n' + f'{message_with_breaks}')

def login_and_post(bs_client, user_handle, user_password, text, embed_external):
    profile = bs_client.login(user_handle, user_password)
    post = bs_client.send_post(text, embed=embed_external)

def main():
    if len(sys.argv) != 3:
        print_usage_and_exit()

    user_handle, user_password = sys.argv[1], sys.argv[2]

    setup_cookies()

    repositories = get_trending_repositories()

    gpt_client = GPTClient()
    bs_client = BSClient()

    for full_url, repo_href, repo_name in repositories:
        print(f'URL: {full_url}\nName: {repo_href}')

        readme_text = get_readme_text(repo_href)
        message = get_repository_description(gpt_client, repo_href, readme_text)
        print(message)

        title, description, image_url = get_link_card_info(full_url)
        print(title, description, image_url, sep='\n')

        embed_external = prepare_embed_external(title, description, full_url)
        text = prepare_text(repo_name, full_url, message)
        print(text)

        login_and_post(bs_client, user_handle, user_password, text, embed_external)

if __name__ == "__main__":
    main()
