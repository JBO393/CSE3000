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

patterns = {
    "string_notation": {
        "prefix": re.compile(r'.*["\'].*:[^:\'"]*:[^:\'"]*\+["\']'),
        "brackets": re.compile(r'.*["\'].*:[^:\'"]*:[\[(\]].*[\])\[]["\']')
    },
    "version": {
        "prefix": re.compile(r'["\'][^:\'"]*\+["\']'),
        "brackets": re.compile(r'["\'][\[(\]].*[\])\[]["\']')
    }
}

range_types = ["prefix", "brackets"]

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
        for range_type in range_types:
            matches = re.findall(patterns["version"][range_type], decoded_toml_file)
            if len(matches) > 0:
                return matches, range_type

    return None, None


def contains_ranges(build_file_list, toml_files_checked):
    decoded_build_file = base64.b64decode(build_file_list[2]).decode("utf-8")
    for line in decoded_build_file.split("\n"):
        stripped = line.strip()

        # Check string notation
        for range_type in range_types:
            if patterns["string_notation"][range_type].match(stripped):
                return stripped, range_type

        if ".kts" in build_file_list[1]:
            # Check map notation Kotlin
            if "group =" in stripped and "name =" in stripped and "version =" in stripped:
                version = stripped.split("version =")[1].strip()
                for range_type in range_types:
                    if patterns["version"][range_type].match(version):
                        return stripped, range_type
        else:
            # Check map notation Groovy
            if "group:" in stripped and "name:" in stripped and "version:" in stripped:
                version = stripped.split("version:")[1].strip()
                for range_type in range_types:
                    if patterns["version"][range_type].match(version):
                        return stripped, range_type

    # If using libs.versions.toml file, check for ranges
    if "libs." in decoded_build_file and build_file_list[0] not in toml_files_checked:
        toml_files_checked.add(build_file_list[0])
        return contains_ranges_toml_file(build_file_list[0])

    return None, None

version_range_repos = set()
ranges_per_repo = dict()
toml_files_checked = set()
variable_part_per_repo = dict()
with (open("data/build_files.txt") as build_files):
    for build_file in build_files:
        if build_file == "\n":
            continue
        build_file_list = ast.literal_eval(build_file)
        repo = build_file_list[0]
        ranges_found, type_found = contains_ranges(build_file_list, toml_files_checked)
        if ranges_found is not None:
            #print(f"{repo}: {ranges_found}")
            version_range_repos.add(repo)

            if repo not in ranges_per_repo:
                ranges_per_repo[repo] = dict()

            num_matches = 1 if isinstance(ranges_found, str) else len(ranges_found)
            ranges_per_repo[repo][type_found] = ranges_per_repo[repo].get(type_found, 0) + num_matches

            # Determine variable part of the version range.
            # This only works for prefix notation ranges in map notation version declarations
            # Other notations are printed and manually analyzed
            variable_part = None
            if type_found == "prefix":
                map_notation_splitted = ranges_found.split("version: ")
                if len(map_notation_splitted) > 1:
                    version = map_notation_splitted[1]
                    version = version.replace("'", "")
                    version_parts = version.split(".")
                    for i in range(len(version_parts)):
                        if version_parts[i] == "+":
                            variable_part = i
                        elif "+" in version_parts[i]:
                            variable_part = 0

            if variable_part is None:
                print(f"Repo: '{repo}' Range: '{ranges_found}'")
            else:
                if repo not in variable_part_per_repo:
                    variable_part_per_repo[repo] = dict()

                variable_part_per_repo[repo][variable_part] = variable_part_per_repo[repo].get(variable_part, 0) + 1


print(version_range_repos)
print(ranges_per_repo)
print("Variable part per repo. 0: Major, 1: Minor, 2: Patch")
print(variable_part_per_repo)