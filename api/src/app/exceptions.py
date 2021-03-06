from fastapi import HTTPException


class InvalidTokenException(HTTPException):  # pragma: no cover
    def __init__(self, headers: dict = None):
        status_code = 401
        detail = 'Requested token is invalid.'
        super().__init__(status_code, detail, headers)


class ExpiredTokenException(HTTPException):  # pragma: no cover
    def __init__(self, headers: dict = None):
        status_code = 400
        detail = 'This token has already expired.'
        super().__init__(status_code, detail, headers)


class UnauthorizedUserException(HTTPException):  # pragma: no cover
    def __init__(self, headers: dict = None):
        status_code = 401
        detail = 'This user is not registered with this app yet.'
        super().__init__(status_code, detail, headers)


class ForbiddenAccessException(HTTPException):  # pragma: no cover
    def __init__(self, headers: dict = None):
        status_code = 403
        detail = 'You do not have permission to access.'
        super().__init__(status_code, detail, headers)


class MissingRequestTokenException(HTTPException):  # pragma: no cover
    def __init__(self, headers: dict = None):
        status_code = 401
        detail = 'Missing request token.'
        super().__init__(status_code, detail, headers)


class UserNotFoundException(HTTPException):  # pragma: no cover
    def __init__(self, headers: dict = None):
        status_code = 404
        detail = 'User not Found.'
        super().__init__(status_code, detail, headers)


class PostNotFoundException(HTTPException):  # pragma: no cover
    def __init__(self, headers: dict = None):
        status_code = 404
        detail = 'Post not Found.'
        super().__init__(status_code, detail, headers)
