import json
import os
import subprocess
import time
import requests
from dotenv import load_dotenv

def detect_java_version(repo, current_folder):
    with open(f"{current_folder}/data/java_versions.json", mode="r") as f:
        java_versions_json = json.load(f)
        return java_versions_json[repo]

def build_repos(repos, current_folder, output_folder):
    load_dotenv()

    java_versions = {8: os.getenv("JAVA8"),
                     11: os.getenv("JAVA11"),
                     17: os.getenv("JAVA17"),
                     21: os.getenv("JAVA21"),
                     23: os.getenv("JAVA23"),
                     24: os.getenv("JAVA24")}
    gradle_path = os.getenv("GRADLE")

    count = 1
    for repo in repos:
        if repo == "CDCgov/prime-simplereport":
            repo = "CDCgov/prime-simplereport/backend"

        print(f"Building repo {count} of {len(repos)}: {repo}")
        os.chdir(f"{current_folder}/data/cloned_repos/{repo}")
        java_version = detect_java_version(repo, current_folder)
        env = os.environ.copy()
        env["JAVA_HOME"] = java_versions[java_version]
        try:
            result = subprocess.run([gradle_path, "build", "--no-daemon"],
                                    capture_output=True, text=True, timeout=600, env=env)

            with open(f"{current_folder}/data/{output_folder}/successful/{repo.replace("/", "+")}.txt", mode="w+") as build_output:
                build_output.write(result.stdout)

            with open(f"{current_folder}/data/{output_folder}/failed/{repo.replace("/", "+")}.txt", mode="w+") as build_output:
                build_output.write(result.stderr)

            if result.returncode == 0:
                print(f"Build succeeded for repo {repo}")
            else:
                print(f"Build failed for repo {repo}")


        except Exception as e:
            print(f"Build failed for repo {repo}. Error: {e}")

        count += 1

def send_api_request(url, headers, repos_left):
    response = requests.get(url, headers=headers)

    while response.status_code == 429 or response.status_code == 403:
        response_headers = response.headers
        if int(response_headers["X-RateLimit-Remaining"]) > 0:
            break

        rate_limit_reset = int(response_headers["x-ratelimit-reset"]) + 2
        formatted_time = time.strftime("%H:%M:%S", time.localtime(rate_limit_reset))
        print(f"Rate limit exceeded. Repos left: {repos_left}. Trying again at {formatted_time}")
        time.sleep(rate_limit_reset - time.time())
        response = requests.get(url, headers=headers)

    return response