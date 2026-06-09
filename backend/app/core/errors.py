class AppError(Exception):
    """Base application exception."""


class ExternalDataSourceError(AppError):
    """Raised when an external data source request fails."""


class MappingError(AppError):
    """Raised when source data cannot be mapped into an application schema."""


class PersistenceError(AppError):
    """Raised when database persistence fails."""


class ConfigurationError(AppError):
    """Raised when required runtime configuration is missing or invalid."""


class NotFoundError(AppError):
    """Raised when a requested real data record cannot be found."""


class AIServiceError(AppError):
    """Raised when an AI service request or response is invalid."""
