import os

from haystack import Pipeline, Document
from haystack.utils.auth import Secret
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.preprocessors.document_splitter import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder
from haystack_integrations.components.embedders.cohere import CohereDocumentEmbedder
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

from project_settings import USE_OLLAMA
from haystack_pipelines.helpers.common import SafeComponent, DOCS_EMBEDDING_BREAKER


def indexing_pipeline(document_store: PgvectorDocumentStore):
    """
    Execute indexing pipeline.

    :param document_store: Configured Haystack document store.
    """

    text_splitter = DocumentSplitter()
    docs_embedder = OllamaDocumentEmbedder(
        model="nomic-embed-text",
        url=os.environ['OLLAMA_BASE_URL'],
    ) if USE_OLLAMA else CohereDocumentEmbedder(
        model="embed-multilingual-v3.0",
        api_key=Secret.from_env_var("COHERE_API_KEY")
    )

    protected_embedder = SafeComponent(docs_embedder, DOCS_EMBEDDING_BREAKER)

    text_writer = DocumentWriter(
        document_store=document_store, policy=DuplicatePolicy.SKIP)

    pipeline = Pipeline()
    pipeline.add_component("splitter", text_splitter)
    pipeline.add_component("embedder", protected_embedder)
    pipeline.add_component("writer", text_writer)

    pipeline.connect("splitter", "embedder")
    pipeline.connect("embedder", "writer")

    return pipeline


def splitting_pipeline() -> Pipeline:
    """
    Execute splitting pipeline.
    """
    text_splitter = DocumentSplitter()

    pipeline = Pipeline()
    pipeline.add_component("splitter", text_splitter)

    return pipeline


def vectorizing_pipeline(document_store: PgvectorDocumentStore) -> Pipeline:
    """
    Execute vectorizing pipeline.

    :param document_store: Configured Haystack document store.
    """
    docs_embedder = OllamaDocumentEmbedder(
        model="nomic-embed-text",
        url=os.environ['OLLAMA_BASE_URL'],
    ) if USE_OLLAMA else CohereDocumentEmbedder(
        model="embed-multilingual-v3.0",
        api_key=Secret.from_env_var("COHERE_API_KEY")
    )

    protected_embedder = SafeComponent(docs_embedder, DOCS_EMBEDDING_BREAKER)

    text_writer = DocumentWriter(
        document_store=document_store, policy=DuplicatePolicy.SKIP)

    pipeline = Pipeline()
    pipeline.add_component("embedder", protected_embedder)
    pipeline.add_component("writer", text_writer)

    pipeline.connect("embedder", "writer")

    return pipeline


if __name__ == "__main__":
    doc = Document(
        content="This is a small demo document used for indexing.",
        id="demo-1",
        meta={},
    )

    # Run splitting to produce document chunks.
    SPLIT_PIPELINE = splitting_pipeline()
    split_result = SPLIT_PIPELINE.run({"splitter": {"documents": [doc]}})
    chunks = split_result["splitter"]["documents"]
    total_chunks = len(chunks)
    print(f"Total chunks: {total_chunks}")

    # Initialize the document store used in this flow.
    # Initialize the document store used in this flow.
    document_store = PgvectorDocumentStore(  # noqa: F841
        table_name="haystack_documents_demo",
        embedding_dimension=768,
        vector_function="cosine_similarity",
        recreate_table=False,
        search_strategy="hnsw",
        keyword_index_name="keyword_index_demo",
    )
    EMBEDDING_PIPELINE = vectorizing_pipeline(document_store)

    batch_size = 64
    processed = 0
    try:
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i + batch_size]
            EMBEDDING_PIPELINE.run({"embedder": {"documents": batch}})
            processed += len(batch)
            progress = round(processed / max(total_chunks, 1) * 100, 2)
            print(f"Progress: {progress}% ({processed}/{total_chunks})")
    finally:
        chunk_ids = [str(chunk.id) for chunk in chunks if chunk.id is not None]
        if chunk_ids:
            document_store.delete_documents(chunk_ids)
            print(f"Rollback: deleted {len(chunk_ids)} chunks")
