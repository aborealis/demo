from typing import Any
import os
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from pytest import MonkeyPatch
from models.orm.user import User
from models.orm.document import DocumentDB
from models.orm.tokens import TokenStats
from services.haystack.docs_indexing import index_doc_with_separator
from services.celery_tasks.helpers.indexing import filter_documents_with_retry
import routes.user_docs_mgmt as docs_mgt_module


os.environ["HAYSTACK_TELEMETRY_ENABLED"] = "false"
os.environ["POSTHOG_DISABLED"] = "true"


def fake_background_task(*args: Any, **kwargs: Any):
    print("Background task called")


class TestUploadMultiple:
    """Test suite for upload multiple."""

    def test_401(self,
                 client: TestClient,
                 path_to_file_with_separator: str,
                 monkeypatch: MonkeyPatch,
                 ):
        """Test 401."""
        monkeypatch.setattr(
            "routes.user_docs_mgmt.index_doc_with_separator",
            fake_background_task,
        )

        with open(path_to_file_with_separator, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload/multiple/",
                files={"file": ("test.txt", f, "text/plain")},
            )

        assert response.status_code == 401

    def test_200(self,
                 client: TestClient,
                 hdr_user: dict,
                 path_to_file_with_separator: str,
                 monkeypatch: MonkeyPatch,
                 ):
        """Test 200."""
        monkeypatch.setattr(
            "routes.user_docs_mgmt.index_doc_with_separator",
            fake_background_task,
        )

        with open(path_to_file_with_separator, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload/multiple/",
                headers=hdr_user,
                files={"file": ("test.txt", f, "text/plain")},
            )

        assert response.status_code == 200

    def test_invalid_file_format_400(self,
                                     client: TestClient,
                                     hdr_user: dict,
                                     path_to_file_with_separator: str,
                                     monkeypatch: MonkeyPatch,
                                     ):
        """Test invalid file format 400."""

        monkeypatch.setattr(
            "routes.user_docs_mgmt.index_doc_with_separator",
            fake_background_task,
        )

        with open(path_to_file_with_separator, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload/multiple/",
                headers=hdr_user,
                files={"file": ("test.txt", f, "application/pdf")},
            )

        assert response.status_code == 400


def test_writes_new_file_with_separator_to_db(
    db_tests: Session,
    txtfile_with_separator: str,
    fake_user: User,
):
    """Test writes new file with separator to db."""
    _ = index_doc_with_separator(
        db_tests,
        txtfile_with_separator,
        similarity=0.9,
        current_user=fake_user,
    )

    rows = db_tests.exec(
        select(DocumentDB)
    ).all()

    assert len(rows)

    chunks = filter_documents_with_retry(filters={})
    assert len(chunks) >= len(rows)

    tokens_row = db_tests.exec(select(TokenStats)).first()
    assert tokens_row is not None
    tokens_spent = tokens_row.tokens_spent
    assert tokens_spent > 0


def test_rewrite_file_with_separator_to_db_similarity_low(
    db_tests: Session,
    txtfile_with_separator: str,
    updated_txtfile_with_separator: str,
    fake_user: User,
):
    """Test rewrite file with separator to db similarity low."""
    _ = index_doc_with_separator(
        db_tests,
        txtfile_with_separator,
        similarity=0.9,
        current_user=fake_user,
    )

    rows_first_write = db_tests.exec(
        select(DocumentDB)
    ).all()

    tokens_row1 = db_tests.exec(select(TokenStats)).first()
    assert tokens_row1 is not None
    tokens_spent1 = tokens_row1.tokens_spent

    _ = index_doc_with_separator(
        db_tests,
        updated_txtfile_with_separator,
        similarity=0.3,
        current_user=fake_user,
    )

    rows_second_write = db_tests.exec(
        select(DocumentDB)
    ).all()

    assert len(rows_first_write) == len(rows_second_write)

    tokens_row2 = db_tests.exec(select(TokenStats)).first()
    assert tokens_row2 is not None
    tokens_spent2 = tokens_row2.tokens_spent
    assert tokens_spent2 > tokens_spent1


def test_rewrite_file_with_separator_to_db_similarity_high(
    db_tests: Session,
    txtfile_with_separator: str,
    updated_txtfile_with_separator: str,
    fake_user: User,
):
    """Test rewrite file with separator to db similarity high."""
    _ = index_doc_with_separator(
        db_tests,
        txtfile_with_separator,
        similarity=0.9,
        current_user=fake_user,
    )

    rows_first_write = db_tests.exec(
        select(DocumentDB)
    ).all()

    _ = index_doc_with_separator(
        db_tests,
        updated_txtfile_with_separator,
        similarity=0.9,
        current_user=fake_user,
    )

    rows_second_write = db_tests.exec(
        select(DocumentDB)
    ).all()

    assert len(rows_first_write) == len(rows_second_write) - 1
