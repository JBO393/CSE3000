import ast
import os
import shutil
import subprocess

from dotenv import load_dotenv

load_dotenv()

def copy_lock_files(destination, lock_files, repos):
    for lock_file in lock_files:
        if lock_file[0] not in repos:
            continue

        lock_file_path = f"data/cloned_repos/{lock_file[0]}/{lock_file[1]}"
        file_name = f"{lock_file[0].replace('/', '+')}+{lock_file[1].replace('/', '+')}"
        if os.path.exists(lock_file_path):
            shutil.copy(lock_file_path, f"data/lock_files/{destination}/{file_name}")
        else:
            print(f"Lock file {lock_file_path} not found")

lock_files = []
repos = set()
current_folder = os.path.dirname(os.path.realpath(__file__))
gradle_path = os.getenv("GRADLE")

with open("data/lock_files.txt", mode="r") as file:
    for line in file:
        lock_file_list = ast.literal_eval(line)
        lock_files.append([lock_file_list[0], lock_file_list[1]])
        repos.add(lock_file_list[0])

# Copy original lock files
copy_lock_files("original", lock_files, repos)

# Re-resolve dependencies
count = 1
successful_repos = set()
for repo in repos:
    print(f"Resolving dependencies for repo {count} of {len(repos)}")
    os.chdir(f"{current_folder}/data/cloned_repos/{repo}")
    try:
        result = subprocess.run([gradle_path, "dependencies", "--update-locks", "*:*", "--no-daemon"],
                                capture_output=True, text=True, timeout=600)

        with open(f"{current_folder}/data/resolve_dependencies_output/successful/{repo.replace("/", "+")}.txt", mode="w+") as build_output:
            build_output.write(result.stdout)

        with open(f"{current_folder}/data/resolve_dependencies_output/failed/{repo.replace("/", "+")}.txt", mode="w+") as build_output:
            build_output.write(result.stderr)

        if result.returncode == 0:
            print(f"Resolve dependencies succeeded for repo {repo}")
            successful_repos.add(repo)
        else:
            print(f"Resolve dependencies failed for repo {repo}")

    except Exception as e:
        print(f"Build failed for repo {repo}. Error: {e}")

    count += 1

os.chdir(current_folder)

# Copy new lock files
copy_lock_files("after_deleting", lock_files, successful_repos)