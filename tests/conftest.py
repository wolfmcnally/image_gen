"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def tmp_image(tmp_path: Path) -> Path:
    """Create a temporary test image file."""
    # Create a minimal valid PNG (1x1 transparent pixel)
    png_data = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    image_path = tmp_path / "test.png"
    image_path.write_bytes(png_data)
    return image_path
