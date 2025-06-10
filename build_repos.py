import ast
import json
import os
import subprocess

from dotenv import load_dotenv

load_dotenv()

repos = set()
count = 1
current_folder = os.path.dirname(os.path.realpath(__file__))
java_versions = {8: os.getenv("JAVA8"),
                 11: os.getenv("JAVA11"),
                 17: os.getenv("JAVA17"),
                 21: os.getenv("JAVA21"),
                 23: os.getenv("JAVA23"),
                 24: os.getenv("JAVA24")}
gradle_path = os.getenv("GRADLE")

# with open("data/lock_files.txt", mode="r") as lock_files:
#     for lock_file in lock_files:
#         lock_file_list = ast.literal_eval(lock_file)
#         repos.add(lock_file_list[0])
#         path = f"data/cloned_repos/{lock_file_list[0]}/{lock_file_list[1]}"
#         if os.path.exists(path):
#             print("Found")
#             # os.remove(path)
#         else:
#             print(f"Could not find lock file '{lock_file_list[0]}/{lock_file_list[1]}'")


def detect_java_version(repo, current_folder):
    with open(f"{current_folder}/data/java_versions.json", mode="r") as f:
        java_versions_json = json.load(f)
        return java_versions_json[repo]


for repo in repos:
    if repo == "jjohannes/understanding-gradle":
        count += 1
        continue
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
        with open(f"{current_folder}/data/build_output/{repo.replace("/", "+")}.txt", mode="w+") as build_output:
            build_output.write(result.stdout)

        with open(f"{current_folder}/data/build_error/{repo.replace("/", "+")}.txt", mode="w+") as build_output:
            build_output.write(result.stderr)

        if result.returncode == 0:
            print(f"Build succeeded for repo {repo}")
        else:
            print(f"Build failed for repo {repo}")
    except Exception as e:
        print(f"Build failed for repo {repo}. Error: {e}")

    count += 1
