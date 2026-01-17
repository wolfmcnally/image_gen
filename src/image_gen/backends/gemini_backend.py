"""Google Gemini image generation backend."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from image_gen.backends.base import ImageBackend, ImageGenConfig, ImageGenResult

if TYPE_CHECKING:
    from google import genai
    from google.genai import types

DEFAULT_MODEL = "gemini-3-pro-image-preview"

# Map pixel dimensions to aspect ratios
SIZE_TO_ASPECT: dict[str, str] = {
    # Square
    "1024x1024": "1:1",
    "1536x1536": "1:1",
    "2048x2048": "1:1",
    # Landscape 16:9
    "1920x1080": "16:9",
    "1280x720": "16:9",
    "3840x2160": "16:9",
    "1344x768": "16:9",
    # Portrait 9:16
    "1080x1920": "9:16",
    "720x1280": "9:16",
    # 4:3
    "1024x768": "4:3",
    "1280x960": "4:3",
    # 3:4
    "768x1024": "3:4",
    "960x1280": "3:4",
    # 21:9 ultrawide
    "2560x1080": "21:9",
    "3440x1440": "21:9",
    "1536x672": "21:9",
}

# Valid aspect ratios that can be passed directly
VALID_ASPECTS = {"1:1", "16:9", "9:16", "4:3", "3:4", "21:9"}

# Quality to resolution mapping
QUALITY_TO_SIZE: dict[str, str] = {"high": "4K", "medium": "2K", "low": "1K"}

# Moderation mapping: OpenAI level -> Gemini threshold
# "low" -> OFF (least restrictive), "auto" -> BLOCK_ONLY_HIGH
MODERATION_TO_THRESHOLD: dict[str, str] = {"low": "OFF", "auto": "BLOCK_ONLY_HIGH"}


class GeminiBackend(ImageBackend):
    """Google Gemini API backend."""

    def __init__(self) -> None:
        try:
            from google import genai as genai_module
            from google.genai import types as types_module
        except ImportError:
            sys.stderr.write("[!] The 'google-genai' package is required for Gemini backend.\n")
            sys.stderr.write("    Install with: pip install google-genai\n")
            sys.exit(1)
        self.genai: genai = genai_module
        self.types: types = types_module
        self.client = genai_module.Client()

    def validate_config(self, config: ImageGenConfig) -> list[str]:
        """Return warnings for unsupported options."""
        warnings: list[str] = []
        if config.transparent:
            warnings.append(
                "--transparent not supported: Gemini cannot generate true alpha transparency"
            )
        if config.count > 1:
            warnings.append(
                f"Gemini generates one image per request; will make {config.count} API calls"
            )
        return warnings

    def _get_safety_settings(self, moderation: str) -> list[Any]:
        """Build safety settings based on moderation level."""
        threshold_name = MODERATION_TO_THRESHOLD.get(moderation, "BLOCK_ONLY_HIGH")
        threshold = getattr(self.types.HarmBlockThreshold, threshold_name)
        # Apply to all harm categories
        return [
            self.types.SafetySetting(
                category=self.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=threshold,
            ),
            self.types.SafetySetting(
                category=self.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=threshold,
            ),
            self.types.SafetySetting(
                category=self.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=threshold,
            ),
            self.types.SafetySetting(
                category=self.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=threshold,
            ),
        ]

    def _parse_size(self, size: str) -> tuple[str, str | None]:
        """Convert size to (aspect_ratio, image_size).

        Returns:
            Tuple of (aspect_ratio, image_size) where image_size is None
            if it should be derived from quality setting.
        """
        # Check if it's a direct aspect ratio
        if size in VALID_ASPECTS:
            return size, None
        # Check if it's a known pixel dimension
        if size in SIZE_TO_ASPECT:
            return SIZE_TO_ASPECT[size], None
        # Try to parse WxH format and compute aspect ratio
        if "x" in size:
            try:
                w, h = map(int, size.lower().split("x"))
                # Find closest matching aspect ratio
                ratio = w / h
                aspects = {
                    1.0: "1:1",
                    16 / 9: "16:9",
                    9 / 16: "9:16",
                    4 / 3: "4:3",
                    3 / 4: "3:4",
                    21 / 9: "21:9",
                }
                closest = min(aspects.keys(), key=lambda x: abs(x - ratio))
                return aspects[closest], None
            except (ValueError, ZeroDivisionError):
                pass
        # Default fallback
        return "1:1", None

    def _extract_images(self, response: Any) -> list[ImageGenResult]:
        """Extract images from Gemini API response."""
        results: list[ImageGenResult] = []
        if not response.candidates:
            return results
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                mime_type = getattr(part.inline_data, "mime_type", "image/png")
                fmt = mime_type.split("/")[-1] if "/" in mime_type else "png"
                results.append(
                    ImageGenResult(
                        image_data=part.inline_data.data,
                        format=fmt,
                    )
                )
        return results

    def _generate_single(
        self, prompt: str, aspect_ratio: str, image_size: str, safety_settings: list[Any]
    ) -> list[ImageGenResult]:
        """Generate a single image from text prompt."""
        response = self.client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=[prompt],
            config=self.types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=self.types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                ),
                safety_settings=safety_settings,
            ),
        )
        return self._extract_images(response)

    def generate(self, config: ImageGenConfig) -> list[ImageGenResult]:
        """Generate images from text prompt."""
        aspect_ratio, _ = self._parse_size(config.size)
        image_size = QUALITY_TO_SIZE[config.quality]
        safety_settings = self._get_safety_settings(config.moderation)

        # Gemini generates one image per request, so loop for count > 1
        results: list[ImageGenResult] = []
        for i in range(config.count):
            if config.count > 1:
                sys.stderr.write(f"  Generating image {i + 1}/{config.count}...\n")
            results.extend(
                self._generate_single(config.prompt, aspect_ratio, image_size, safety_settings)
            )
        return results

    def edit(self, config: ImageGenConfig) -> list[ImageGenResult]:
        """Edit images using prompt and input images."""
        try:
            from PIL import Image
        except ImportError:
            sys.stderr.write("[!] The 'Pillow' package is required for Gemini image editing.\n")
            sys.stderr.write("    Install with: pip install Pillow\n")
            sys.exit(1)

        aspect_ratio, _ = self._parse_size(config.size)
        image_size = QUALITY_TO_SIZE[config.quality]
        safety_settings = self._get_safety_settings(config.moderation)

        # Build contents with prompt and images
        contents: list[Any] = [config.prompt]
        for img_path in config.images:
            contents.append(Image.open(img_path))

        response = self.client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=contents,
            config=self.types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=self.types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                ),
                safety_settings=safety_settings,
            ),
        )
        return self._extract_images(response)
