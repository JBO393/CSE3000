import ast
import base64

with open("data/poms.json") as poms:
    poms_list = ast.literal_eval(poms.read())

for pom in poms_list:
    name = list(pom.keys())[0]
    content = base64.b64decode(pom[name])

    with open(f"data/poms/{name.replace('/', '+')}.xml", mode="wb+") as file:
        file.write(content)