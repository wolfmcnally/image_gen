"""Custom exceptions for image-gen."""


class ImageGenError(Exception):
    """Base exception for image-gen errors."""


class ConfigurationError(ImageGenError):
    """Raised when configuration is invalid."""


class APIKeyError(ConfigurationError):
    """Raised when required API key is missing."""


class BackendError(ImageGenError):
    """Raised when a backend operation fails."""


class ValidationError(ImageGenError):
    """Raised when input validation fails."""
