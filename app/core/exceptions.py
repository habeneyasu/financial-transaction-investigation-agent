"""Custom exceptions for the financial transaction investigation agent."""


class InvestigationError(Exception):
    """Base exception for investigation-related errors."""
    pass


class DatabaseError(InvestigationError):
    """Exception raised when database operations fail."""
    pass


class CustomerNotFoundError(InvestigationError):
    """Exception raised when a customer is not found."""
    pass


class AccountNotFoundError(InvestigationError):
    """Exception raised when an account is not found."""
    pass


class TransactionNotFoundError(InvestigationError):
    """Exception raised when a transaction is not found."""
    pass


class InvestigationCaseNotFoundError(InvestigationError):
    """Exception raised when an investigation case is not found."""
    pass


class MCPError(InvestigationError):
    """Exception raised when MCP operations fail."""
    pass


class LLMError(InvestigationError):
    """Exception raised when LLM operations fail."""
    pass


class ApplicationValidationError(InvestigationError):
    """Exception raised when data validation fails."""
    pass


class InvestigationTimeoutError(InvestigationError):
    """Exception raised when investigation exceeds timeout."""
    pass


class InvestigationMaxStepsError(InvestigationError):
    """Exception raised when investigation exceeds maximum steps."""
    pass
