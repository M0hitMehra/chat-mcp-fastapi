from typing import Optional


class AppError(Exception):
    """
    Custom application exception.

    Usage:
        raise AppError(
            message="Company not found",
            status_code=404,
            error_code="COMPANY_NOT_FOUND",
        )
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_SERVER_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.success = False

        super().__init__(message)
