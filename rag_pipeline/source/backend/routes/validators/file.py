from fastapi import UploadFile
import routes.helpers.response_constants as rc


def get_text_from_txt_file_or_400(file: UploadFile) -> str:
    """
    Get text from txt file or 400.
    """

    content = file.file.read()
    text = ""

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        rc.ERR_400_INVALID_TEXTFILE_ENCODING.raise_exception()

    return text
