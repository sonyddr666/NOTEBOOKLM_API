"""Core module for NotebookLM client wrapper."""

from .client import get_client, NotebookLMClientWrapper
from .exceptions import (
    NotebookLMError,
    AuthenticationError,
    NotebookNotFoundError,
    SourceError,
    StudioError,
    RateLimitError,
)

__all__ = [
    "get_client",
    "NotebookLMClientWrapper",
    "NotebookLMError",
    "AuthenticationError",
    "NotebookNotFoundError",
    "SourceError",
    "StudioError",
    "RateLimitError",
]
