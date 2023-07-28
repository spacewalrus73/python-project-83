from urllib.parse import urlparse


def normalize(url: str) -> str:
    """Returns url with schema and netlock only"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
