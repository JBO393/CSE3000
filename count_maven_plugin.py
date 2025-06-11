import os

from dotenv import load_dotenv

from shared_functions import send_api_request

load_dotenv()

# Create a .env file in the same directory as this script and add PAT=<your personal access token>
pat = os.getenv("PAT")
headers = {"Authorization": f"Bearer {pat}"}

current_page = 1
num_pages = 1
count = 0
num_files = 1000
found_repos = set()

while current_page <= num_pages and current_page <= 10:
    url = f"https://api.github.com/search/code?q=dependencies-lock.json+in:path&per_page=100&page={current_page}"
    response = send_api_request(url, headers, num_files - count)
    response_json = response.json()
    num_files = response_json["total_count"]
    num_pages = int(num_files / 100) + 1
    found_files = response_json["items"]
    current_page += 1

    for file in found_files:
        if count % 50 == 0:
            print(f"Repo {count} of {num_files}")
        found_repos.add(file["repository"]["full_name"])
        count += 1

print(len(found_repos))
