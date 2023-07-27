import requests
from bs4 import BeautifulSoup


def get_status_code(url: str) -> int | None:
    """Returns status code if the page is available, otherwise - None"""
    if is_available(url):
        response = requests.get(url)
        return response.status_code
    return None


def is_available(url: str) -> bool:
    """Predicate exception handler. Checks if the page is available"""
    try:
        requests.get(url)
    except requests.exceptions.RequestException:
        return False

    response = requests.get(url)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return False

    return True


def parse(url: str) -> dict:
    """Parser function that extracts seo-parameters from html page"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    meta_link = soup.find('meta', attrs={"name": 'description'})
    description = meta_link["content"]
    return {
        "title": soup.title.get_text() if soup.title else '',
        "h1": soup.h1.get_text() if soup.h1 else '',
        "description": description if description else ''
    }
