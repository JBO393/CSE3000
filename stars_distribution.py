import os

import requests
from dotenv import load_dotenv

load_dotenv()

# Create a .env file in the same directory as this script and add PAT=<your personal access token>
pat = os.getenv("PAT")
headers = {"Authorization": f"Bearer {pat}"}

current_page = 1
num_pages = 1
count = 0
stars_dict = dict()

while current_page <= num_pages and current_page <= 10:
    url = f"https://api.github.com/search/code?q=/gradle.lockfile+in:path&per_page=100&page={current_page}"
    response = requests.get(url, headers=headers)
    response_json = response.json()
    num_repos = response_json["total_count"]
    num_pages = int(num_repos / 100) + 1
    repos = response_json["items"]
    current_page += 1

    for repo in repos:
        if count % 50 == 0:
            print(f"Repo {count} of {num_repos}")

        name = repo["repository"]["full_name"]
        url = f"https://api.github.com/repos/{name}"
        response = requests.get(url, headers=headers)

        stars = response.json()["stargazers_count"]
        stars_dict[stars] = stars_dict.get(stars, 0) + 1

        count += 1

print(stars_dict)
