from src.exceptions import AppException


class InvalidStateCompare(AppException):
    def __init__(self):
        message = "Invalid state compare"
        super().__init__(message, status_code=400)

class NotFoundToken(AppException):
    def __init__(self):
        message = "Refresh token for user not found or inactive"
        super().__init__(message, status_code=401)