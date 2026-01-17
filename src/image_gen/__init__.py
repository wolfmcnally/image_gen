"""image-gen - Generate or edit images using OpenAI GPT or Google Gemini APIs."""

from image_gen.backends import ImageBackend, ImageGenConfig, ImageGenResult, get_backend

__version__ = "0.1.0"
__all__ = ["ImageBackend", "ImageGenConfig", "ImageGenResult", "__version__", "get_backend"]
