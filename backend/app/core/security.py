from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(
    key_func=get_remote_address
)


MAX_URL_LENGTH = 2048
MAX_TEXT_LENGTH = 10000
MAX_IMAGE_SIZE = 5 * 1024 * 1024

ALLOWED_IMAGE_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
}


def validate_text_length(text: str) -> str:
    text = text.strip()

    if not text:
        raise ValueError("Input cannot be empty.")

    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(
            f"Text exceeds the {MAX_TEXT_LENGTH} character limit."
        )

    return text


def validate_url_length(url: str) -> str:
    url = url.strip()

    if not url:
        raise ValueError("URL cannot be empty.")

    if len(url) > MAX_URL_LENGTH:
        raise ValueError(
            f"URL exceeds the {MAX_URL_LENGTH} character limit."
        )

    return url
