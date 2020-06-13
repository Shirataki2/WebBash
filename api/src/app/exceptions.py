from fastapi import HTTPException


class InvalidTokenException(HTTPException):
    def __init__(self, headers: dict = None):
        status_code = 401
        detail = 'Requested token is invalid.'
        super().__init__(status_code, detail, headers)


class ExpiredTokenException(HTTPException):
    def __init__(self, headers: dict = None):
        status_code = 400
        detail = 'This token has already expired.'
        super().__init__(status_code, detail, headers)


class UnauthorizedUserException(HTTPException):
    def __init__(self, headers: dict = None):
        status_code = 401
        detail = 'This user is not registered with this app yet.'
        super().__init__(status_code, detail, headers)


class UserNotFoundException(HTTPException):
    def __init__(self, headers: dict = None):
        status_code = 404
        detail = 'User not Found.'
        super().__init__(status_code, detail, headers)
