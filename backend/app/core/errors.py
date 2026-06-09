class AppError(Exception):
    """Base application exception."""


class ExternalDataSourceError(AppError):
    """Raised when an external data source request fails."""


class MappingError(AppError):
    """Raised when source data cannot be mapped into an application schema."""


class PersistenceError(AppError):
    """Raised when database persistence fails."""
