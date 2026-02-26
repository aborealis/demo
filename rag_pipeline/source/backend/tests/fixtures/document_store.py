import os
import pytest
from pytest import MonkeyPatch
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack.utils.auth import Secret
from project_settings import USE_OLLAMA

from fixtures.common import DocStoreParams


@pytest.fixture()
def set_env_variable(monkeypatch: MonkeyPatch):
    """Set env variable."""
    monkeypatch.setenv("TEST_MODE", "1")


@pytest.fixture(autouse=True)
def document_store_test(monkeypatch: MonkeyPatch):
    """Document store test."""
    import haystack_pipelines.initializator as pipes

    os.environ["PG_CONN_STR_TEST"] = (
        os.environ["PG_CONN_STR"]
        .replace("dbname=chatbot", "dbname=tests")
    )

    document_store_params = DocStoreParams(
        table_name="ollama",
        dimension=768
    ) if USE_OLLAMA else DocStoreParams(
        table_name="cohere_v3",
        dimension=1024
    )

    DOCUMENT_STORE_TESTS = PgvectorDocumentStore(
        connection_string=Secret.from_env_var("PG_CONN_STR_TEST"),
        table_name=f"haystack_documents_{document_store_params.table_name}",
        embedding_dimension=document_store_params.dimension,
        vector_function="cosine_similarity",
        recreate_table=False,
        search_strategy="hnsw",
        keyword_index_name=f"keyword_index_{document_store_params.table_name}"
    )

    monkeypatch.setattr(
        pipes, "DOCUMENT_STORE",
        DOCUMENT_STORE_TESTS
    )

    monkeypatch.setattr(
        pipes,
        "INDEXING_PIPELINE",
        pipes.indexing_pipeline(DOCUMENT_STORE_TESTS),
    )

    monkeypatch.setattr(
        pipes,
        "CHAT_SEARCH_PIPELINE",
        pipes.srs.search_pipeline(DOCUMENT_STORE_TESTS),
    )

    monkeypatch.setattr(
        pipes,
        "SEARCH_PIPELINE",
        pipes.search_pipeline(DOCUMENT_STORE_TESTS),
    )

    monkeypatch.setattr(
        pipes,
        "EMBEDDING_PIPELINE",
        pipes.vectorizing_pipeline(DOCUMENT_STORE_TESTS),
    )
