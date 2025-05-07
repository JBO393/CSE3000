import ast
import base64

with open("data/poms.json") as poms:

    for pom in poms:
        if pom == "\n":
            continue
        pom_list = ast.literal_eval(pom)
        name = pom_list[0]
        content = base64.b64decode(pom_list[1])

        with open(f"data/poms/{name.replace('/', '+')}.xml", mode="wb+") as file:
            file.write(content)
