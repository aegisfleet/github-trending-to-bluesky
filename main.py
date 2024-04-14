import requests
import sys
import g4f
from bs4 import BeautifulSoup
from g4f.client import Client as GPTClient
from atproto import Client as BSClient, client_utils, models

def print_usage_and_exit():
    print("使用法: python script.py <ユーザーハンドル> <パスワード>")
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
        repositories.append((full_url, name))

    return repositories

def get_repository_description(gpt_client, url):
    response = gpt_client.chat.completions.create(
        model="gpt-3.5-turbo",
        provider=g4f.Provider.Liaobots,
        messages=[{"role": "user", "content": f"{url} このリポジトリは誰がいつどこで使うものか250文字以下で説明して欲しい。回答は日本語で簡素にすること。"}],
    )
    return response.choices[0].message.content

def login_and_post(bs_client, user_handle, user_password, text, embed_external):
    profile = bs_client.login(user_handle, user_password)
    post = bs_client.send_post(text, embed=embed_external)

def main():
    if len(sys.argv) != 3:
        print_usage_and_exit()

    user_handle, user_password = sys.argv[1], sys.argv[2]
    repositories = get_trending_repositories()

    gpt_client = GPTClient()
    bs_client = BSClient()

    for full_url, repo_name in repositories:
        print(f'URL: {full_url}\nName: {repo_name}')

        message = get_repository_description(gpt_client, full_url)
        print(message)

        title, description, image_url = get_link_card_info(full_url)
        print(title, description, image_url, sep='\n')

        embed_external = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                title=title,
                description=description,
                uri=full_url
            )
        )

        message_with_breaks = message.replace('\n', '').replace('。', '。\n')
        text = client_utils.TextBuilder().text('今日のGitHubトレンド\n\n').link(f'{repo_name}', f'{full_url}').text('\n' + f'{message_with_breaks}')
        print(text)

        login_and_post(bs_client, user_handle, user_password, text, embed_external)

if __name__ == "__main__":
    main()
