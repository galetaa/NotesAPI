class ValidationError(Exception):
    """Base class for validation errors."""

    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserAlreadyExistsError(ValidationError):
    """Exception raised when a user already exists."""

    def __init__(self, message="User already exists.", status_code=409):
        super().__init__(message, status_code)


class UserDoesNotExistsError(ValidationError):
    """Exception raised when a user does not exist."""

    def __init__(self, message="User doesn't exist.", status_code=404):
        super().__init__(message, status_code)


class NoneCredentialsError(ValidationError):
    """Exception raised for invalid username or password."""

    def __init__(self, message="Username and password are required.", status_code=401):
        super().__init__(message, status_code)


class NoneNoteParamsError(ValidationError):
    """Exception raised for invalid text or title."""

    def __init__(self, message="Text and title are required.", status_code=401):
        super().__init__(message, status_code)


class InvalidUsernameError(ValidationError):
    """Exception raised for invalid username."""

    def __init__(self, message="Username is invalid.", status_code=400):
        super().__init__(message, status_code)


class InvalidPasswordError(ValidationError):
    """Exception raised for invalid password."""

    def __init__(self, message="Password is invalid.", status_code=400):
        super().__init__(message, status_code)


class InvalidTextError(ValidationError):
    """Exception raised for invalid note text."""

    def __init__(self, message="Text is invalid.", status_code=400):
        super().__init__(message, status_code)


class InvalidTitleError(ValidationError):
    """Exception raised for invalid note title."""

    def __init__(self, message="Title is invalid.", status_code=400):
        super().__init__(message, status_code)


class InvalidUserID(ValidationError):
    """Exception raised for invalid userid."""

    def __init__(self, message="User ID is invalid.", status_code=400):
        super().__init__(message, status_code)


class InvalidNoteID(ValidationError):
    """Exception raised for invalid noteid."""

    def __init__(self, message="Note ID is invalid.", status_code=400):
        super().__init__(message, status_code)


class IncorrectPasswordError(ValidationError):
    """Exception raised for incorrect password."""

    def __init__(self, message="Password is incorrect.", status_code=401):
        super().__init__(message, status_code)


class AccessDeniedError(ValidationError):
    """Exception raised when you haven't permission to access."""

    def __init__(self, message="Access denied.", status_code=403):
        super().__init__(message, status_code)


class NoteDoesNotExistsError(ValidationError):
    """Exception raised when a note does not exist."""

    def __init__(self, message="Note doesn't exist.", status_code=404):
        super().__init__(message, status_code)


class OutdatedNoteError(ValidationError):
    """Exception raised when a note does not exist."""

    def __init__(self, message="This note is outdated.", status_code=400):
        super().__init__(message, status_code)


class InvalidDateGapError(ValidationError):
    """Exception raised when start date later than end date."""

    def __init__(self, message="Start date later than end date.", status_code=400):
        super().__init__(message, status_code)


class InvalidPageParamsError(ValidationError):
    """Exception raised when start date later than end date."""

    def __init__(self, message="Invalid page params.", status_code=400):
        super().__init__(message, status_code)


class ThereIsNoData(ValidationError):
    """Exception raised when there is no any data to get."""

    def __init__(self, message="there is no any data to get.", status_code=400):
        super().__init__(message, status_code)
