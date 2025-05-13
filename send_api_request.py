import time
from datetime import datetime, timedelta

import requests


def send_api_request(url, headers, repos_left):
    response = requests.get(url, headers=headers)

    while response.status_code == 429 or response.status_code == 403:
        print(f"Rate limit exceeded. Repos left: {repos_left}. Trying again at {(datetime.now() + timedelta(seconds=600)).strftime("%H:%M:%S")}")
        time.sleep(600)
        response = requests.get(url, headers=headers)

    return response