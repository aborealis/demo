"""Module description."""
from typing import Any
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from models.orm.user import User
from models.orm.document import DocumentDB
from pytest import MonkeyPatch

from models.orm.document import DocStatus
from services.haystack.docs_indexing import (
    index_doc_with_separator,
    filter_documents_with_retry,
)
from redis import Redis as RedisSync
import project_setings as proj_settings


class TestSingleFile:
    """Test suite for single file."""

    def test_progress_in_redis(self,
                               db_tests: Session,
                               client: TestClient,
                               txtfile_with_separator: str,
                               fake_user: User,
                               hdr_user: dict[str, str]):

        index_doc_with_separator(
            db_tests,
            txtfile_with_separator,
            similarity=0.9,
            current_user=fake_user,
        )

        document = db_tests.exec(
            select(DocumentDB)
        ).first()

        assert document is not None
        assert document.id == 1

        long_text = "some new content"

        redis = RedisSync.from_url(
            proj_settings.REDIS_URL,
            decode_responses=True
        )

        redis.flushall()

        response = client.patch(
            f"/api/v1/documents/update/content/{document.id}/",
            json={
                "content": long_text,
            },
            headers=hdr_user,
        )

        assert response.status_code == 200

        progress = redis.get(f"indexing:{1}:progress")

        assert progress == "100"

    def test_read_progress(self,
                           db_tests: Session,
                           client: TestClient,
                           txtfile_with_separator: str,
                           fake_user: User,
                           hdr_user: dict[str, str]):
        """Test read progress."""
        _ = index_doc_with_separator(
            db_tests,
            txtfile_with_separator,
            similarity=0.9,
            current_user=fake_user,
        )

        with db_tests:
            document = db_tests.exec(
                select(DocumentDB)
            ).first()

            assert document is not None

            client.patch(
                f"/api/v1/documents/update/content/{document.id}/",
                json={
                    "content": "placeholder",
                },
                headers=hdr_user,
            )

            result = client.get(
                f"/api/v1/documents/status/{document.id}/",
                headers=hdr_user,
            )
            assert result.json() == {
                "status": "ready",
                "progress": 100
            }

    def test_update_content(self,
                            db_tests: Session,
                            client: TestClient,
                            txtfile_with_separator: str,
                            fake_user: User,
                            hdr_user: dict[str, str]):
        """Test update content."""
        _ = index_doc_with_separator(
            db_tests,
            txtfile_with_separator,
            similarity=0.9,
            current_user=fake_user,
        )

        with db_tests:
            document = db_tests.exec(
                select(DocumentDB)
            ).first()

            assert document is not None

            client.patch(
                f"/api/v1/documents/update/content/{document.id}/",
                json={
                    "content": "placeholder",
                    "name": "placeholder",
                },
                headers=hdr_user,
            )

            result = client.get(
                "/api/v1/documents/",
                headers=hdr_user,
            )

            doc = [
                r for r in result.json()["documents"]
                if r["id"] == document.id
            ][0]

            assert doc["name"] == "placeholder"

    def test_update_content_exception_sets_failed(
        self,
        db_tests: Session,
        client: TestClient,
        txtfile_with_separator: str,
        fake_user: User,
        hdr_user: dict[str, str],
        monkeypatch: MonkeyPatch,
    ):
        """Test update content exception sets failed."""
        _ = index_doc_with_separator(
            db_tests,
            txtfile_with_separator,
            similarity=0.9,
            current_user=fake_user,
        )

        document: DocumentDB = db_tests.exec(select(DocumentDB)).first()
        assert document.status == DocStatus.READY

        filters = {
            "field": "meta.parent_doc_id",
            "operator": "==",
            "value": document.id
        }
        chunks = filter_documents_with_retry(filters)
        assert len(chunks)

        def crash_split(*args: Any, **kwargs: Any):
            raise RuntimeError("Simulated split crash")

        import services.celery_tasks.helpers.indexing as loc
        monkeypatch.setattr(
            f"{loc.__name__}.pipes.EMBEDDING_PIPELINE.run",
            crash_split
        )

        client.patch(
            f"/api/v1/documents/update/content/{document.id}/",
            json={
                "content": "Crash text",
            },
            headers=hdr_user,
        )

        db_tests.expire_all()
        updated_document: DocumentDB = db_tests.get(
            DocumentDB, document.id)

        assert updated_document.status == DocStatus.FAILED

        chunks = filter_documents_with_retry(filters)
        assert len(chunks) == 0
