class NotFoundError(Exception):
    """Raised when a requested entity is not found."""


class ValidationError(Exception):
    """Raised when incoming data does not pass business validation."""
