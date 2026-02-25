"""Custom exceptions for NotebookLM API and Bot."""


class NotebookLMError(Exception):
    """Base exception for NotebookLM errors."""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
            }
        }


class AuthenticationError(NotebookLMError):
    """Authentication error with NotebookLM."""
    
    def __init__(self, message: str = "Authentication failed. Please run 'nlm login' to authenticate."):
        super().__init__(message, code="AUTHENTICATION_ERROR")


class NotebookNotFoundError(NotebookLMError):
    """Notebook not found error."""
    
    def __init__(self, notebook_id: str):
        super().__init__(
            f"Notebook with ID '{notebook_id}' not found",
            code="NOTEBOOK_NOT_FOUND"
        )
        self.notebook_id = notebook_id


class SourceError(NotebookLMError):
    """Source-related error."""
    
    def __init__(self, message: str, source_id: str = None):
        super().__init__(message, code="SOURCE_ERROR")
        self.source_id = source_id


class StudioError(NotebookLMError):
    """Studio content generation error."""
    
    def __init__(self, message: str, artifact_type: str = None):
        super().__init__(message, code="STUDIO_ERROR")
        self.artifact_type = artifact_type


class RateLimitError(NotebookLMError):
    """Rate limit exceeded error."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            f"Rate limit exceeded. Please try again in {retry_after} seconds.",
            code="RATE_LIMIT_EXCEEDED"
        )
        self.retry_after = retry_after


class ValidationError(NotebookLMError):
    """Validation error."""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class ResearchError(NotebookLMError):
    """Research operation error."""
    
    def __init__(self, message: str, research_id: str = None):
        super().__init__(message, code="RESEARCH_ERROR")
        self.research_id = research_id


class ShareError(NotebookLMError):
    """Sharing operation error."""
    
    def __init__(self, message: str):
        super().__init__(message, code="SHARE_ERROR")


class NoteError(NotebookLMError):
    """Note operation error."""
    
    def __init__(self, message: str, note_id: str = None):
        super().__init__(message, code="NOTE_ERROR")
        self.note_id = note_id
