"""Abstract base class and common types for image generation backends."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ImageGenConfig:
    """Unified configuration for image generation."""

    prompt: str
    images: tuple[Path, ...]
    quality: str  # "high", "medium", "low"
    size: str  # "1024x1024", "16:9", etc.
    count: int
    transparent: bool
    moderation: str  # "auto", "low"

    def __init__(
        self,
        prompt: str,
        images: list[Path] | tuple[Path, ...],
        quality: str,
        size: str,
        count: int,
        transparent: bool,
        moderation: str,
    ) -> None:
        object.__setattr__(self, "prompt", prompt)
        object.__setattr__(self, "images", tuple(images))
        object.__setattr__(self, "quality", quality)
        object.__setattr__(self, "size", size)
        object.__setattr__(self, "count", count)
        object.__setattr__(self, "transparent", transparent)
        object.__setattr__(self, "moderation", moderation)


@dataclass(frozen=True, slots=True)
class ImageGenResult:
    """Result from image generation."""

    image_data: bytes
    format: str  # "png", "jpeg", etc.


class ImageBackend(ABC):
    """Abstract base class for image generation backends."""

    @abstractmethod
    def validate_config(self, config: ImageGenConfig) -> list[str]:
        """Return list of warnings for unsupported options."""

    @abstractmethod
    def generate(self, config: ImageGenConfig) -> list[ImageGenResult]:
        """Generate images from text prompt. Returns list of results."""

    @abstractmethod
    def edit(self, config: ImageGenConfig) -> list[ImageGenResult]:
        """Edit images using prompt and input images. Returns list of results."""
