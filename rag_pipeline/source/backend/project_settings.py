import os
from configparser import ConfigParser
from pathlib import Path


CONFIG_PATH = Path(__file__).with_name("app_config.ini")
config = ConfigParser()
loaded_files = config.read(CONFIG_PATH)
if not loaded_files:
    raise RuntimeError(
        f"Configuration file '{CONFIG_PATH}' was not found or cannot be read."
    )
try:
    IS_DEBUG = config["app_mode"]["debug"] == "1"
    USE_OLLAMA = config["app_mode"]["ollama"] == "1"

    ACCESS_TOKEN_EXPIRE_MINUTES = int(config["auth"]["token_exp_minutes"])

    REDIS_URL = config["redis"]["redis_url"]
    REDIS_URL_TEST = config["redis"]["redis_url_test"]
    REDIS_URL_BACKEND = config["redis"]["redis_url_backend"]
    DEFAULT_TTL_SECONDS = int(config["redis"]["ttl_sec"])
    DEFAULT_TTL_BUFFER_SECONDS = int(config["redis"]["ttl_buffer_sec"])
    DEFAULT_TTL_LOCK_SECONDS = int(config["redis"]["ttl_lock_sec"])

    CHAT_WINDOW_SIZE = int(config["chat"]["window_size"])  # Initialize `CHAT_WINDOW_SIZE` using `int`.
    MAX_CONNECTIONS_TOTAL = int(config["chat"]["max_connections_total"])
    MAX_CONNECTIONS_PER_ORG = int(config["chat"]["max_connections_per_org"])
    IDLE_TIMEOUT = int(config["chat"]["idle_timeout_sec"])
    MAX_SEND_FREQ = int(config["chat"]["max_send_frequency_persec"])
    SEND_TIME_WINDOW = int(config["chat"]["send_time_window_sec"])
    MAX_MESSAGES_TO_MEASURE_SEND_LIMIT = int(
        config["chat"]["max_messages_to_measure_sent_rate_limit"])
    MAX_SEND_TIME_BEFORE_RETRY = int(config["chat"]["max_send_time_before_retry"])
    MAX_BUFFERED_OUTGOING_MESSAGES = int(
        config["chat"]["max_buffered_outgoing_messages"])
except KeyError as exc:
    raise RuntimeError(
        f"Missing required configuration key/section in '{CONFIG_PATH}': {exc}"
    ) from exc
except ValueError as exc:
    raise RuntimeError(
        f"Invalid numeric configuration value in '{CONFIG_PATH}': {exc}"
    ) from exc


def is_app_under_test() -> bool:
    return os.getenv("TEST_MODE", None) == "1"
