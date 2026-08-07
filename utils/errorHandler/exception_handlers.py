from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from utils.errorHandler.error_handler import AppError


async def app_error_handler(
    request: Request,
    exc: AppError,
):
    """
    Handles explicitly raised application errors.
    """

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "errorCode": exc.error_code,
        },
    )
