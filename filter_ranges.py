import ast
import base64
import os
import re

from dotenv import load_dotenv

from shared_functions import send_api_request

load_dotenv()

# Create a .env file in the same directory as this script and add PAT=<your personal access token>
pat = os.getenv("PAT")
headers = {"Authorization": f"Bearer {pat}"}

patterns = [
    re.compile(r'.*["\'].*:[^:\'"]*:[^:\'"]*\+["\']'), # Match 2.+, 1.3.+, etc.
    re.compile(r'.*["\'].*:[^:\'"]*:[\[(\]].*[\])\[]["\']') # Match [1.3, 1.8), (1.3, 1.8], etc.
]

version_patterns = [
    re.compile(r'["\'][^:\'"]*\+["\']'),    # Match 2.+, 1.3.+, etc.
    re.compile(r'["\'][\[(\]].*[\])\[]["\']')    # Match [1.3, 1.8), (1.3, 1.8], etc.
]


def contains_ranges_toml_file(name):
    url = f"https://api.github.com/search/code?q=libs.versions.toml+in:path+repo:{name}"
    response = send_api_request(url, headers, 1)
    response_json = response.json()
    if response_json["total_count"] == 0 or response_json["total_count"] > 1:
        print(f"Error: {name} has {response_json['total_count']} libs.versions.toml files")
    else:
        path = response_json["items"][0]["path"]
        url = f"https://api.github.com/repos/{name}/contents/{path}"
        response = send_api_request(url, headers, 1)
        response_json = response.json()
        decoded_toml_file = base64.b64decode(response_json["content"]).decode("utf-8")
        for pattern in version_patterns:
            matches = re.findall(pattern, decoded_toml_file)
            if len(matches) > 0:
                return True
    return False


def contains_ranges(build_file_list):
    decoded_build_file = base64.b64decode(build_file_list[2]).decode("utf-8")
    for line in decoded_build_file.split("\n"):
        stripped = line.strip()

        # Check string notation
        for pattern in patterns:
            if pattern.match(stripped):
                return True

        if ".kts" in build_file_list[1]:
            # Check map notation Kotlin
            if "group =" in stripped and "name =" in stripped and "version =" in stripped:
                version = stripped.split("version =")[1].strip()
                for pattern in version_patterns:
                    if pattern.match(version):
                        return True
        else:
            # Check map notation Groovy
            if "group:" in stripped and "name:" in stripped and "version:" in stripped:
                version = stripped.split("version:")[1].strip()
                for pattern in version_patterns:
                    if pattern.match(version):
                        return True

    # If using libs.versions.toml file, check for ranges
    if "libs." in decoded_build_file:
        if contains_ranges_toml_file(build_file_list[0]):
            return True

    return False

version_range_repos = set()
with open("data/build_files.txt") as build_files:
    for build_file in build_files:
        if build_file == "\n":
            continue
        build_file_list = ast.literal_eval(build_file)
        if build_file_list[0] in version_range_repos:
            continue
        if contains_ranges(build_file_list):
            print(build_file_list[0:2])
            version_range_repos.add(build_file_list[0])

print(version_range_repos)