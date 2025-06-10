import os

from dotenv import load_dotenv
import json

from send_api_request import send_api_request

load_dotenv()

# Create a .env file in the same directory as this script and add PAT=<your personal access token>
pat = os.getenv("PAT")
headers = {"Authorization": f"Bearer {pat}"}

with open("data/repos.json", encoding="utf-8") as repos_file:
    repos_json = json.load(repos_file)
    repos = repos_json["items"]

all_gradle_repos = []
count = 0
num_gradle_repos = 0
num_locking_repos = 0

for repo in repos:
    languages = map(lambda x : x["language"], repo["metrics"])

    if "Gradle" in languages:
        all_gradle_repos.append(repo["name"])
        num_gradle_repos += 1

def get_locking_repos(gradle_repos):
    global count
    global num_gradle_repos
    global num_locking_repos
    if count % 50 == 0:
        print(f"Repo {count} of {num_gradle_repos}. Locking repos: {num_locking_repos}")

    gradle_repos_joined = "+OR+repo:".join(gradle_repos)
    url = f"https://api.github.com/search/code?q=filename:gradle.lockfile+repo:{gradle_repos_joined}"
    response = send_api_request(url, headers, num_gradle_repos - count)
    if response.status_code != 200:
        half = int(len(gradle_repos / 2))
        locking_repos_left = get_locking_repos(gradle_repos[:half])
        locking_repos_right = get_locking_repos(gradle_repos[half:])
        return locking_repos_left.union(locking_repos_right)


    response_json = response.json()
    locking_repos = set()

    for found_file in response_json["items"]:
        locking_repos.add(found_file["repository"]["full_name"])

    num_locking_repos += len(locking_repos)
    count += len(gradle_repos)
    return locking_repos

all_locking_repos = set()
for n in range(0, len(all_gradle_repos), 20):
    all_locking_repos.update(get_locking_repos(all_gradle_repos[n:n + 20]))

print(f"Locking repos: {len(all_locking_repos)}")
print(all_locking_repos)