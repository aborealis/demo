from typing import cast
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from .indexing_pipeline import indexing_pipeline, vectorizing_pipeline, splitting_pipeline
from .search_pipeline import search_pipeline
from .one_request_chat import one_request_chat_pipeline
from .lang_detector import lang_detection
from .translate_pipeline import translate_pipeline
from .search_queries_comparison import search_queries_comparison_pipeline
from .user_context import user_context_pipeline
from .goodbye import goodbye_pipeline
from project_settings import USE_OLLAMA
import haystack_pipelines.stage_rag_search as srs

# Initialize the document store used in this flow.
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


# Initialize the document store used in this flow.
INDEXING_PIPELINE = indexing_pipeline(DOCUMENT_STORE)
SPLIT_PIPELINE = splitting_pipeline()
EMBEDDING_PIPELINE = vectorizing_pipeline(DOCUMENT_STORE)
SEARCH_PIPELINE = search_pipeline(DOCUMENT_STORE)
ONE_REQUEST_PIPELINE = one_request_chat_pipeline()
LANG_DETECTION_PIPELINE = lang_detection()
CHAT_SEARCH_PIPELINE = srs.search_pipeline(DOCUMENT_STORE)
ANSWER_FORMULATION_PIPELINE = srs.answer_formulation_pipeline()
TRANSLATION_PIPELINE = translate_pipeline()
SEARCH_QUERIES_COMPARISON_PIPELINE = search_queries_comparison_pipeline()
USER_CONTEXT_PIPELINE = user_context_pipeline()
GOOFBYE_PIPELINE = goodbye_pipeline()
