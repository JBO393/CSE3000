import os
import time

from dotenv import load_dotenv
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
poms = []
response_codes = dict()

for repo in repos:
    name = repo["name"]
    response = requests.get(f"https://api.github.com/repos/{name}/contents/pom.xml", headers=headers)
    while response.status_code == 429:
        print(f"Rate limit exceeded. Repos left: {len(repos) - count}. Sleeping for 10 minutes.")
        time.sleep(600)
        response = requests.get(f"https://api.github.com/repos/{name}/contents/pom.xml", headers=headers)
    count += 1
    if response.status_code == 200:
        response_json = json.loads(response.text)
        poms.append({name: response_json["content"]})
    else:
        print(f"Error: {response.status_code} for {name}")

    response_codes[response.status_code] = response_codes.get(response.status_code, 0) + 1

with open("data/poms.json", mode="w+") as poms_file:
    poms_file.write(json.dumps(poms))

print(response_codes)

