import pytest

from app.engines.image_engine import (
    MAX_IMAGE_SIZE,
    extract_text_from_image,
)
from app.engines.text_engine import analyze_text


def test_empty_text_rejected():
    with pytest.raises(ValueError):
        analyze_text("")


def test_oversized_text_rejected():
    oversized_text = "A" * 10001

    with pytest.raises(ValueError):
        analyze_text(oversized_text)


def test_unsupported_image_type_rejected():
    with pytest.raises(ValueError):
        extract_text_from_image(
            b"fake-image",
            "application/pdf",
        )


def test_empty_image_rejected():
    with pytest.raises(ValueError):
        extract_text_from_image(
            b"",
            "image/png",
        )


def test_oversized_image_rejected():
    oversized_image = b"x" * (
        MAX_IMAGE_SIZE + 1
    )

    with pytest.raises(ValueError):
        extract_text_from_image(
            oversized_image,
            "image/png",
        )


def test_malformed_image_rejected():
    with pytest.raises(ValueError):
        extract_text_from_image(
            b"This is not actually an image.",
            "image/png",
        )
