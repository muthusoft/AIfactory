"""
Custom exceptions for the AI Software Factory.
"""


class AIFactoryException(Exception):
    """Base exception for AI Factory."""
    pass


class ConfigurationException(AIFactoryException):
    """Exception raised for configuration errors."""
    pass


class LLMException(AIFactoryException):
    """Exception raised for LLM-related errors."""
    pass


class ValidationException(AIFactoryException):
    """Exception raised for validation errors."""
    pass


class DatabaseException(AIFactoryException):
    """Exception raised for database errors."""
    pass


class ArtifactException(AIFactoryException):
    """Exception raised for artifact errors."""
    pass


class PipelineException(AIFactoryException):
    """Exception raised for pipeline execution errors."""
    pass


class AgentException(AIFactoryException):
    """Exception raised for agent errors."""
    pass
