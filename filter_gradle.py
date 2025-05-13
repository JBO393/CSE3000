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

with open("data/build_files.json", mode="w+") as build_json_file:
    build_json_file.write("")

with open("data/lock_files.json", mode="w+") as lock_json_file:
    lock_json_file.write("")

with open("data/build_files.json", mode="a+") as build_json_file:
    with open("data/lock_files.json", mode="a+") as lock_json_file:
        for repo in repos:
            name = repo["name"]
            url = f"https://api.github.com/repos/{name}/contents/build.gradle"
            response = send_api_request(url, headers, len(repos) - count)

            if response.status_code == 200:
                response_json = json.loads(response.text)
                build_file_list = [name, response_json["content"]]
                build_json_file.write(f"{build_file_list}\n")

                lock_url = f"https://api.github.com/repos/{name}/contents/gradle.lockfile"
                lock_response = send_api_request(lock_url, headers, len(repos) - count)
                if lock_response.status_code == 200:
                    lock_json = json.loads(lock_response.text)
                    lock_file_list = [name, lock_json["content"]]
                    lock_json_file.write(f"{lock_file_list}\n")

            count += 1
            if count % 50 == 0:
                print(f"Repo {count} of {len(repos)}")

            response_codes[response.status_code] = response_codes.get(response.status_code, 0) + 1

print(response_codes)