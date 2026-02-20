import os
import base64

APP_ADMIN_USERNAME = os.environ["APP_ADMIN_USER"]
APP_ADMIN_NAME = os.environ.get("APP_ADMIN_NAME", "Default User")
APP_ADMIN_HASHED_PASSWORD = base64.b64decode(
    os.environ["APP_ADMIN_HASHED_PASSWORD"]
).decode("utf-8")
