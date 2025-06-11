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

with open("data/lock_files.txt", mode="w+") as lock_files:
    lock_files.write("")

with open("data/build_files.txt", mode="w+") as build_files:
    build_files.write("")

lock_files = open("data/lock_files.txt", mode="a+")
build_files = open("data/build_files.txt", mode="a+")

while current_page <= num_pages and current_page <= 10:
    url = f"https://api.github.com/search/code?q=/gradle.lockfile+in:path&per_page=100&page={current_page}"
    response = send_api_request(url, headers, num_files - count)
    response_json = response.json()
    num_files = response_json["total_count"]
    num_pages = int(num_files / 100) + 1
    found_files = response_json["items"]
    current_page += 1

    for file in found_files:
        if count % 50 == 0:
            print(f"Repo {count} of {num_files}")

        name = file["repository"]["full_name"]
        url = f"https://api.github.com/repos/{name}"
        response = send_api_request(url, headers, num_files - count)

        stars = int(response.json()["stargazers_count"])
        language = response.json()["language"]
        if stars >= 10 and language == "Java":
            lock_file_path = file["path"]
            build_file_path = lock_file_path.replace("gradle.lockfile", "build.gradle")
            lock_file_url = f"https://api.github.com/repos/{name}/contents/{lock_file_path}"
            lock_file_response = send_api_request(lock_file_url, headers, num_files - count)

            build_file_url = f"https://api.github.com/repos/{name}/contents/{build_file_path}"
            build_file_response = send_api_request(build_file_url, headers, num_files - count)

            if build_file_response.status_code == 404:
                build_file_path = lock_file_path.replace("gradle.lockfile", "build.gradle.kts")
                build_file_url = f"https://api.github.com/repos/{name}/contents/{build_file_path}"
                build_file_response = send_api_request(build_file_url, headers, num_files - count)

            if build_file_response.status_code == 200:
                build_file_list = [name, build_file_path, build_file_response.json()["content"]]
                build_files.write(f"{build_file_list}\n")

                lock_file_list = [name, lock_file_path, lock_file_response.json()["content"]]
                lock_files.write(f"{lock_file_list}\n")

            else:
                print(f"No build file found for {name}, {build_file_path}")

        count += 1

lock_files.close()
build_files.close()