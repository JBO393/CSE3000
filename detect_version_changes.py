import ast

from semantic_version import Version

change_dict = {
    0: "no change",
    1: "added",
    2: "patch",
    3: "minor",
    4: "major",
    5: "removed"
}
repos = set()
lock_files = []
changed_versions = dict()
# {
#     "repo1": {
#         "dependency1" = "max_diff",
#         "dependency2" = "max_diff",
#         "dependency3" = "max_diff"
#         },
#     "repo2": {
#         "dependency1" = "max_diff",
#         "dependency2" = "max_diff",
#         "dependency3" = "max_diff"
#         }
# }

with open("data/successfully_resolved.txt", mode="r") as f:
    for repo in f:
        repo_name = repo.strip()
        repos.add(repo_name)
        changed_versions[repo_name] = dict()

with open("data/lock_files.txt", mode="r") as f:
    for lock_file in f:
        lock_file_list = ast.literal_eval(lock_file)
        if lock_file_list[0] in repos:
            lock_files.append([lock_file_list[0], lock_file_list[1]])

def parse_version(line):
    parts = line.split(":")
    if len(parts) >= 3:
        dependency = f"{parts[0]}:{parts[1]}"
        version_and_configurations = parts[2].split("=")
        version = version_and_configurations[0]
        configurations = version_and_configurations[1].strip().split(",")
        try:
            return Version.coerce(version), dependency, configurations
        except ValueError:
            # Try Google API version notation
            version_splitted = version.split("-")
            if len(version_splitted) == 3 and "rev" in version_splitted[1]:
                version = version_splitted[2]
                return Version.coerce(version), dependency, configurations

            print(f"Invalid version '{version}' for dependency {dependency}")

    return None, None, None

def compare_versions(old_version, new_version):
    if new_version.major > old_version.major:
        return 4
    if new_version.minor > old_version.minor:
        return 3
    if new_version.patch > old_version.patch:
        return 2

    return 0

for lock_file in lock_files:
    lock_file_name = f"{lock_file[0].replace("/", "+")}+{lock_file[1].replace("/", "+")}"
    repo_name = lock_file[0]
    original_versions = dict()

    with open(f"data/lock_files/original/{lock_file_name}", mode="r") as f:
        for line in f:
            version, dependency, configurations = parse_version(line)
            if version is not None:
                if dependency not in original_versions:
                    original_versions[dependency] = dict()

                for configuration in configurations:
                    original_versions[dependency][configuration] = version


    new_dependencies = set()

    with open(f"data/lock_files/after_deleting/{lock_file_name}", mode="r") as f:
        for line in f:
            version, dependency, configurations = parse_version(line)

            if version is None:
                continue

            new_dependencies.add(dependency)

            if dependency not in changed_versions[repo_name]:
                changed_versions[repo_name][dependency] = 0

            if dependency not in original_versions:
                max_diff = max(changed_versions[repo_name][dependency], 1)
                changed_versions[repo_name][dependency] = max_diff
                continue

            for configuration in configurations:
                if configuration not in original_versions[dependency]:
                    max_diff = max(changed_versions[repo_name][dependency], 1)
                    continue

                if version != original_versions[dependency][configuration]:
                    new_diff = compare_versions(original_versions[dependency][configuration], version)
                    max_diff = max(changed_versions[repo_name][dependency], new_diff)
                    changed_versions[repo_name][dependency] = max_diff

    for dependency in original_versions.keys():
        if dependency not in new_dependencies:
            changed_versions[repo_name][dependency] = 5


# For every repo, count number of major, minor, patch, removed, added
changes_per_repo = dict()

for repo in changed_versions.keys():
    changes_per_repo[repo] = dict()

    for dependency in changed_versions[repo].keys():
        change = changed_versions[repo][dependency]
        change_name = change_dict[change]
        changes_per_repo[repo][change_name] = changes_per_repo[repo].get(change_name, 0) + 1

#For every dependency, count number of major, minor, patch, removed, added
changes_per_dependency = dict()

for repo in changed_versions.values():
    for dependency in repo.keys():
        change = repo[dependency]
        change_name = change_dict[change]
        if change_name != "no change":
            if dependency not in changes_per_dependency:
                changes_per_dependency[dependency] = dict()
            changes_per_dependency[dependency][change_name] = changes_per_dependency[dependency].get(change_name, 0) + 1

print(changes_per_repo)

for dependency in changes_per_dependency.keys():
    if sum(changes_per_dependency[dependency].values()) > 1:
        print(f"'{dependency}': {changes_per_dependency[dependency]}")

total_changes = dict()
for repo in changes_per_repo.values():
    for change in repo.keys():
        total_changes[change] = total_changes.get(change, 0) + repo[change]

print(total_changes)
