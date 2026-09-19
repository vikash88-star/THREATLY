from io import BytesIO

import pytesseract
from PIL import Image

from app.core.security import (
    ALLOWED_IMAGE_TYPES,
    MAX_IMAGE_SIZE,
)


def extract_text_from_image(
    image_bytes: bytes,
    content_type: str,
) -> dict:

    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            "Unsupported image type. "
            "Allowed types: PNG, JPEG, WEBP."
        )

    if not image_bytes:
        raise ValueError("Uploaded image is empty.")

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError(
            "Image exceeds the 5 MB upload limit."
        )

    try:
        image = Image.open(BytesIO(image_bytes))

        image.verify()

        image = Image.open(BytesIO(image_bytes))

        image.load()

    except Exception as exc:
        raise ValueError(
            "The uploaded file is not a valid image."
        ) from exc

    extracted_text = pytesseract.image_to_string(image)

    return {
        "text": extracted_text.strip(),
        "text_length": len(extracted_text.strip()),
        "image_format": image.format,
        "image_width": image.width,
        "image_height": image.height,
    }