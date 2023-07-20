import requests


def check_availability(url: str) -> int:

    try:
        requests.get(url)
    except requests.exceptions.RequestException:
        return 0

    response = requests.get(url)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return 0

    return response.status_code
