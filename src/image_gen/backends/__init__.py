"""Image generation backends package."""

from image_gen.backends.base import ImageBackend, ImageGenConfig, ImageGenResult


def get_backend(api_name: str) -> ImageBackend:
    """Get the appropriate backend for the given API name.

    Args:
        api_name: "gpt" for OpenAI or "gemini" for Google Gemini

    Returns:
        An initialized ImageBackend instance

    Raises:
        ValueError: If api_name is not recognized
    """
    if api_name == "gpt":
        from image_gen.backends.openai_backend import OpenAIBackend

        return OpenAIBackend()
    elif api_name == "gemini":
        from image_gen.backends.gemini_backend import GeminiBackend

        return GeminiBackend()
    else:
        raise ValueError(f"Unknown API backend: {api_name}")


__all__ = ["ImageBackend", "ImageGenConfig", "ImageGenResult", "get_backend"]
