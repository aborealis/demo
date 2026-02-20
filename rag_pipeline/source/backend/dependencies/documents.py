from fastapi import UploadFile

import routes.helpers.response_constants as rc

MAX_SNIFF_BYTES = 4096
ALLOWED_MIME_TYPES_TXT = {"text/plain"}


def validate_file_type_txt(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_MIME_TYPES_TXT:
        rc.ERR_400_INVALID_FILE_TYPE.raise_exception()

    stream = file.file
    start_pos = stream.tell()
    sniff = stream.read(MAX_SNIFF_BYTES)
    stream.seek(start_pos)

    if b"\x00" in sniff:
        rc.ERR_400_INVALID_FILE_TYPE.raise_exception()

    try:
        sniff.decode("utf-8")
    except UnicodeDecodeError:
        rc.ERR_400_INVALID_FILE_TYPE.raise_exception()

    return "text"
