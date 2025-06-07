import ast
import git

repos = set()
count = 1

with open("data/lock_files.txt", mode="r") as f:
    for line in f:
        lock_file_list = ast.literal_eval(line)
        repos.add(lock_file_list[0])

for repo in repos:
    print(f"Cloning repo {count} of {len(repos)}")
    git.Repo.clone_from(f"https://www.github.com/{repo}", f"data/cloned_repos/{repo}")
    count += 1