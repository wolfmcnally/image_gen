"""OpenAI/GPT image generation backend."""

from __future__ import annotations

import base64
import sys
import urllib.request
from typing import TYPE_CHECKING, Any

from image_gen.backends.base import ImageBackend, ImageGenConfig, ImageGenResult

if TYPE_CHECKING:
    from pathlib import Path

    import openai

DEFAULT_MODEL = "gpt-image-1.5"


def get_media_type(path: Path) -> str:
    """Get the MIME type for an image file."""
    ext = path.suffix.lower()
    if ext in {".jpg", ".jpeg"}:
        return "image/jpeg"
    elif ext == ".png":
        return "image/png"
    elif ext == ".webp":
        return "image/webp"
    return f"image/{ext[1:]}"


class OpenAIBackend(ImageBackend):
    """OpenAI GPT Image API backend."""

    def __init__(self) -> None:
        try:
            import openai as openai_module
        except ImportError:
            sys.stderr.write("[!] The 'openai' package is required for GPT backend.\n")
            sys.stderr.write("    Install with: pip install --upgrade openai\n")
            sys.exit(1)
        self.client: openai.OpenAI = openai_module.OpenAI()

    def validate_config(self, config: ImageGenConfig) -> list[str]:  # noqa: ARG002
        """OpenAI supports all options, no warnings needed."""
        return []

    def _decode_result(self, result: Any) -> ImageGenResult:
        """Decode a single result from the API response."""
        if hasattr(result, "b64_json") and result.b64_json:
            image_data = base64.standard_b64decode(result.b64_json)
        elif hasattr(result, "url") and result.url:
            with urllib.request.urlopen(result.url) as resp:
                image_data = resp.read()
        else:
            raise ValueError("Unexpected response format from OpenAI API")
        return ImageGenResult(image_data=image_data, format="png")

    def generate(self, config: ImageGenConfig) -> list[ImageGenResult]:
        """Generate images from text prompt."""
        response = self.client.images.generate(
            model=DEFAULT_MODEL,
            prompt=config.prompt,
            size=config.size,
            quality=config.quality,
            n=config.count,
            background="transparent" if config.transparent else "opaque",
            moderation=config.moderation,
        )
        return [self._decode_result(r) for r in response.data]

    def edit(self, config: ImageGenConfig) -> list[ImageGenResult]:
        """Edit images using prompt and input images."""
        image_tuples = [(p.name, p.read_bytes(), get_media_type(p)) for p in config.images]
        response = self.client.images.edit(
            model=DEFAULT_MODEL,
            image=image_tuples,
            prompt=config.prompt,
            size=config.size,
            quality=config.quality,
            n=config.count,
        )
        return [self._decode_result(r) for r in response.data]
