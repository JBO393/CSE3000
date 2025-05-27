import ast
import base64

with open("data/build_files.txt") as build_files:
    for build_file in build_files:
        if build_file == "\n":
            continue
        build_file_list = ast.literal_eval(build_file)
        name = build_file_list[0]
        path = build_file_list[1]
        content = base64.b64decode(build_file_list[2])

        with open(f"data/build_files/{name.replace('/', '+')}+{path.replace('/', '+')}", mode="wb+") as file:
            file.write(content)

with open("data/lock_files.txt") as lock_files:
    for lock_file in lock_files:
        if lock_file == "\n":
            continue
        lock_file_list = ast.literal_eval(lock_file)
        name = lock_file_list[0]
        path = lock_file_list[1]
        content = base64.b64decode(lock_file_list[2])

        with open(f"data/lock_files/{name.replace('/', '+')}+{path.replace('/', '+')}", mode="wb+") as file:
            file.write(content)