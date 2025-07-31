"""
Exception classes for the Alinea SDK.
"""


class AlineaError(Exception):
    """Base exception class for all Alinea SDK errors."""
    pass


class CoordinationError(AlineaError):
    """Raised when coordination operations fail."""
    pass


class ResourceLockError(CoordinationError):
    """Raised when resource lock operations fail."""
    pass


class IntentionError(CoordinationError):
    """Raised when intention registration or execution fails."""
    pass


class PatternError(AlineaError):
    """Raised when pattern operations fail."""
    pass


class CausalityError(AlineaError):
    """Raised when causality analysis fails."""
    pass


class WorldStateError(AlineaError):
    """Raised when world state operations fail."""
    pass


class MemoryError(AlineaError):
    """Raised when memory operations fail."""
    pass


class APIError(AlineaError):
    """Raised when API calls fail."""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class TimeoutError(AlineaError):
    """Raised when operations timeout."""
    pass


class AuthenticationError(APIError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(APIError):
    """Raised when authorization fails."""
    pass
