from fastapi import status

from routes.helpers.openapi_responce_constructor import ApiError, MessageResponse


ERR_500_INVALID_USER_FORMAT = ApiError(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    description="Wrong User Format",
    detail="The user {user details} has wrong format in DB",
)


ERR_401_INVALID_USERNAME = ApiError(
    status_code=status.HTTP_401_UNAUTHORIZED,
    description="Invalid username",
    detail="Invalid username",
    headers={"WWW-Authenticate": "Bearer"},
)

ERR_401_INVALID_PASSWORD = ApiError(
    status_code=status.HTTP_401_UNAUTHORIZED,
    description="Invalid password",
    detail="Invalid password",
    headers={"WWW-Authenticate": "Bearer"},
)

ERR_401_NO_TOKEN = ApiError(
    status_code=status.HTTP_401_UNAUTHORIZED,
    description="No authorization token provided",
    detail="Not authenticated",
)

ERR_401_INVALID_TOKEN = ApiError(
    status_code=status.HTTP_401_UNAUTHORIZED,
    description="Invalid authorization token",
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


ERR_400_INVALID_FILE_TYPE = ApiError(
    status_code=status.HTTP_400_BAD_REQUEST,
    description="Invalid file type",
    detail="Unsupported file type. Only text files are allowed",
)

ERR_400_INVALID_TEXTFILE_ENCODING = ApiError(
    status_code=status.HTTP_400_BAD_REQUEST,
    description="Invalid encoding for text file",
    detail="Text file must be UTF-8 encoded",
)

ERR_404_NO_DOCUMENT_IN_ORGANIZATION = ApiError(
    status_code=status.HTTP_404_NOT_FOUND,
    description="No document with the given ID is found",
    detail="Document with the given ID was not found",
)


ERR_400_INVALID_CHAT_PASSPORT_ID = ApiError(
    status_code=status.HTTP_400_BAD_REQUEST,
    description="Invalid chat passport",
    detail="Invalid chat passport id",
)


OK_200_MESSAGE_DOCUMENT_DELETED = MessageResponse("Document deleted")
OK_200_MESSAGE_INDEXING_STARTED = MessageResponse(
    "Documents uploaded and indexing started",
)
