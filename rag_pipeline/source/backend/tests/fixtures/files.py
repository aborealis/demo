import os
from pathlib import Path
import pytest


@pytest.fixture
def path_to_file_with_separator():
    """Path to file with separator."""
    return os.path.join("tests", "data", "structured_dialogues.txt")


@pytest.fixture
def path_to_updated_file_with_separator():
    """Path to updated file with separator."""
    return os.path.join("tests", "data", "structured_dialogues_updated.txt")


@pytest.fixture
def txtfile_with_separator(path_to_file_with_separator: str):
    """Txtfile with separator."""
    path = Path(path_to_file_with_separator)
    return path.read_text(encoding="utf-8")


@pytest.fixture
def updated_txtfile_with_separator(path_to_updated_file_with_separator: str):
    """Updated txtfile with separator."""
    path = Path(path_to_updated_file_with_separator)
    return path.read_text(encoding="utf-8")
