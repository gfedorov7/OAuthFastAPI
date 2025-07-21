from src.types import ID


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class NotFoundRecordByIdError(AppException):
    def __init__(self, model_name: str, entity_id: ID):
        message = f"The {model_name} id {entity_id} does not exist."
        super().__init__(message, status_code=404)

class InternalServerError(AppException):
    def __init__(self):
        message = f"Internal Server Error"
        super().__init__(message, status_code=500)
        
class UnauthorizeError(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=401)