import requests
from bs4 import BeautifulSoup

import artifact_utils

def get_trending_repositories(url="https://github.com/trending", count=5):
    previous_repositories = artifact_utils.load_previous_results()
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    repo_elements = soup.find_all("h2", class_="h3 lh-condensed")

    repositories = []
    for repo_element in repo_elements[:10]:
        if len(repositories) >= count:
            break
        a_tag = repo_element.find("a")
        href = a_tag["href"]
        full_url = f"https://github.com{href}"
        if full_url not in previous_repositories:
            name = href[1:]
            repositories.append((full_url, name))

    artifact_utils.save_results(repositories)
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
