import ast
import os

from shared_functions import build_repos

repos = set()
current_folder = os.path.dirname(os.path.realpath(__file__))
with open("data/successful_builds.txt", mode="r") as f:
    for line in f:
        repo = line.strip()
        repos.add(repo)

with open("data/lock_files.txt", mode="r") as lock_files:
    for lock_file in lock_files:
        lock_file_list = ast.literal_eval(lock_file)
        if lock_file_list[0] in repos:
            path = f"data/cloned_repos/{lock_file_list[0]}/{lock_file_list[1]}"
            if os.path.exists(path):
                os.remove(path)
                print(f"Lock file '{lock_file_list[0]}/{lock_file_list[1]}' removed")
            else:
                print(f"Could not find lock file '{lock_file_list[0]}/{lock_file_list[1]}'")

build_repos(repos, current_folder, "build_output_after_deleting")