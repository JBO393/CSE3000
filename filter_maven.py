import os
import time

from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
import json

load_dotenv()

# Create a .env file in the same directory as this script and add PAT=<your personal access token>
pat = os.getenv("PAT")
headers = {"Authorization": f"Bearer {pat}"}

with open("data/repos.json", encoding="utf-8") as repos_file:
    repos_json = json.load(repos_file)
    repos = repos_json["items"]

count = 0
response_codes = dict()

with open("data/poms.json", mode="w+") as poms_file:
    poms_file.write("")

with open("data/poms.json", mode="a+") as poms_file:
    for repo in repos:
        name = repo["name"]
        response = requests.get(f"https://api.github.com/repos/{name}/contents/pom.xml", headers=headers)

        while response.status_code == 429 or response.status_code == 403:
            print(f"Rate limit exceeded. Repos left: {len(repos) - count}. Trying again at {(datetime.now() + timedelta(seconds=600)).strftime("%H:%M:%S")}")
            time.sleep(600)
            response = requests.get(f"https://api.github.com/repos/{name}/contents/pom.xml", headers=headers)

        count += 1
        if response.status_code == 200:
            response_json = json.loads(response.text)
            pom_list = [name, response_json["content"]]
            poms_file.write(f"{pom_list}\n")

        if count % 50 == 0:
            print(f"Repo {count} of {len(repos)}")

        response_codes[response.status_code] = response_codes.get(response.status_code, 0) + 1

print(response_codes)
