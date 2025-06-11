import ast
import os

from shared_functions import build_repos

repos = set()
current_folder = os.path.dirname(os.path.realpath(__file__))

with open("data/lock_files.txt", mode="r") as lock_files:
    for lock_file in lock_files:
        lock_file_list = ast.literal_eval(lock_file)
        repos.add(lock_file_list[0])

build_repos(repos, current_folder, "build_output")
