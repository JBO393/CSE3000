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

count = 0
response_codes = dict()
exceptions = []

with open("data/build_files.txt", mode="w+") as build_file:
    build_file.write("")

with open("data/lock_files.txt", mode="w+") as lock_file:
    lock_file.write("")

build_file = open("data/build_files.txt", mode="a+")
lock_file = open("data/lock_files.txt", mode="a+")

for repo in repos:
    if count % 50 == 0:
        print(f"Repo {count} of {len(repos)}")

    name = repo["name"]
    languages = map(lambda x : x["language"], repo["metrics"])

    if "Gradle" not in languages:
        count += 1
        continue

    url = f"https://api.github.com/repos/{name}/contents/build.gradle"
    response = send_api_request(url, headers, len(repos) - count)

    if response.status_code == 200:
        response_json = json.loads(response.text)
        build_file_list = [name, response_json["content"]]
        build_file.write(f"{build_file_list}\n")

        lock_url = f"https://api.github.com/repos/{name}/contents/gradle.lockfile"
        lock_response = send_api_request(lock_url, headers, len(repos) - count)
        if lock_response.status_code == 200:
            lock_json = json.loads(lock_response.text)
            lock_file_list = [name, lock_json["content"]]
            lock_file.write(f"{lock_file_list}\n")

    count += 1

    response_codes[response.status_code] = response_codes.get(response.status_code, 0) + 1

    if response.status_code != 200 and response.status_code != 404:
        exceptions.append(name)

build_file.close()
lock_file.close()

print(exceptions)
print(response_codes)