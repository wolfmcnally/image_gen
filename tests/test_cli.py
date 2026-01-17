"""Tests for CLI module."""

from pathlib import Path

import pytest

from image_gen.backends.base import ImageGenConfig, ImageGenResult


class TestImageGenConfig:
    """Tests for ImageGenConfig dataclass."""

    def test_config_creation(self) -> None:
        """Test creating a configuration."""
        config = ImageGenConfig(
            prompt="test prompt",
            images=[],
            quality="high",
            size="1024x1024",
            count=1,
            transparent=False,
            moderation="low",
        )
        assert config.prompt == "test prompt"
        assert config.images == ()
        assert config.quality == "high"
        assert config.size == "1024x1024"
        assert config.count == 1
        assert config.transparent is False
        assert config.moderation == "low"

    def test_config_with_images(self, tmp_image: Path) -> None:
        """Test creating a configuration with image paths."""
        config = ImageGenConfig(
            prompt="edit this",
            images=[tmp_image],
            quality="medium",
            size="16:9",
            count=2,
            transparent=True,
            moderation="auto",
        )
        assert len(config.images) == 1
        assert config.images[0] == tmp_image

    def test_config_is_frozen(self) -> None:
        """Test that config is immutable."""
        config = ImageGenConfig(
            prompt="test",
            images=[],
            quality="high",
            size="1024x1024",
            count=1,
            transparent=False,
            moderation="low",
        )
        with pytest.raises(AttributeError):
            config.prompt = "modified"  # type: ignore[misc]


class TestImageGenResult:
    """Tests for ImageGenResult dataclass."""

    def test_result_creation(self) -> None:
        """Test creating a result."""
        result = ImageGenResult(image_data=b"test data", format="png")
        assert result.image_data == b"test data"
        assert result.format == "png"

    def test_result_is_frozen(self) -> None:
        """Test that result is immutable."""
        result = ImageGenResult(image_data=b"test", format="png")
        with pytest.raises(AttributeError):
            result.format = "jpeg"  # type: ignore[misc]
