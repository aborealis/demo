import os
from typing import cast
from pprint import pprint
from haystack import Document
from haystack import Pipeline
from haystack.utils.auth import Secret
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack_integrations.components.embedders.cohere import CohereTextEmbedder
from project_settings import USE_OLLAMA
from haystack_pipelines.helpers.common import SafeComponent, TEXT_EMBEDDING_BREAKER


def search_pipeline(document_store: PgvectorDocumentStore):
    """
    Search pipeline.

    :param document_store: Configured Haystack document store.
    """
    query_embedder = OllamaTextEmbedder(
        model="nomic-embed-text",
        url=os.environ['OLLAMA_BASE_URL'],
    ) if USE_OLLAMA else CohereTextEmbedder(
        model="embed-multilingual-v3.0",
        api_key=Secret.from_env_var("COHERE_API_KEY")
    )

    safe_embedder = SafeComponent(query_embedder, TEXT_EMBEDDING_BREAKER)

    retriever = PgvectorEmbeddingRetriever(document_store=document_store)
    pipeline = Pipeline()

    pipeline.add_component("query_embedder", safe_embedder)
    pipeline.add_component("retriever", retriever)

    pipeline.connect("query_embedder.embedding", "retriever.query_embedding")
    return pipeline


if __name__ == "__main__":
    document_store_params: dict[str, str | int] = {
        "table_name": "ollama",
        "dimension": 768
    } if USE_OLLAMA else {
        "table_name": "cohere_v3",
        "dimension": 1024
    }

    DOCUMENT_STORE = PgvectorDocumentStore(
        table_name=f"haystack_documents_{document_store_params['table_name']}",
        embedding_dimension=cast(int, document_store_params["dimension"]),
        vector_function="cosine_similarity",
        recreate_table=False,
        search_strategy="hnsw",
        keyword_index_name=f"keyword_index_{document_store_params['table_name']}"
    )
    SEARCH_PIPELINE = search_pipeline(DOCUMENT_STORE)
    QUERY = "How can I reset my password?"

    result = SEARCH_PIPELINE.run({
        "query_embedder": {"text": QUERY},
        "retriever": {"top_k": 5}
    })

    chunks: list[Document] = result["retriever"]["documents"]

    chunks.sort(key=lambda x: x.score if x.score else 0.0, reverse=True)

    doc_ids = list({
        chunk.meta["parent_doc_id"]
        for chunk in chunks
        if chunk.meta.get("parent_doc_id", None)
    })

    pprint(chunks)
    print(doc_ids)
