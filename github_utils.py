import requests
from bs4 import BeautifulSoup

def get_trending_repositories(url="https://github.com/trending", count=5):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    repo_elements = soup.find_all("h2", class_="h3 lh-condensed")[:count]

    repositories = []
    for repo_element in repo_elements:
        a_tag = repo_element.find("a")
        href = a_tag["href"]
        name = href[1:]
        full_url = f"https://github.com{href}"
        repositories.append((full_url, name))

    return repositories

def get_readme_text(repo_name):
    readme_urls = [
        f"https://raw.githubusercontent.com/{repo_name}/main/README.md",
        f"https://raw.githubusercontent.com/{repo_name}/master/README.md"
    ]
    for url in readme_urls:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text[:2000]
    return ''
