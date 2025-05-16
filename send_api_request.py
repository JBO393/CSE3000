import time

import requests


def send_api_request(url, headers, repos_left):
    response = requests.get(url, headers=headers)

    while response.status_code == 429 or response.status_code == 403:
        response_headers = response.headers
        if int(response_headers["X-RateLimit-Remaining"]) > 0:
            break
        rate_limit_reset = int(response_headers["x-ratelimit-reset"]) + 10
        formatted_time = time.strftime("%H:%M:%S", time.localtime(rate_limit_reset))
        print(f"Rate limit exceeded. Repos left: {repos_left}. Trying again at {formatted_time}")
        time.sleep(time.localtime(rate_limit_reset) - time.localtime())
        response = requests.get(url, headers=headers)

    return response