from validators.url import url


def validate(address: str) -> list:
    """Complex validator for url address"""
    errors = []
    if not url_empty(address):
        errors.append("URL обязателен")
    if not url_has_normal_length(address):
        errors.append("URL превышает 255 символов")
    if not url_valid(address):
        errors.append("Некорректный URL")
    return errors


def url_empty(address: str) -> bool:
    """
    Simple predicate function that returns True if url not empty string,
    False if not
    """
    return address != ''


def url_has_normal_length(address: str) -> bool:
    """Simple predicate function that returns True
        if address length < 255, False if not"""
    return len(address) < 255


def url_valid(address: str) -> bool:
    """Library predicate function which returns True
    if address is valid, False if not"""
    return url(address)
