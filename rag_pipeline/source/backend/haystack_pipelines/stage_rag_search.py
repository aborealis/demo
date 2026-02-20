import os
from typing import cast
import json

from haystack import Pipeline, Document, component
from haystack.utils.auth import Secret
from haystack.dataclasses import ChatMessage
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.embedders.cohere import CohereTextEmbedder
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever
from haystack_pipelines.helpers.common import serialize_chat_messages, extract_json, pipeline_constructor
from project_settings import USE_OLLAMA
from haystack_pipelines.helpers.common import SafeComponent, TEXT_EMBEDDING_BREAKER
import haystack_pipelines.helpers.templates as tmpl


from models.schemas.document import QueryContext
from models.orm.document import DocumentDB as DocumentDB


def search_chunks(query: QueryContext,
                  search_pipeline: Pipeline,
                  ) -> list[str]:
    """
    Search chunks.

    :param query: User search query.
    :param search_pipeline: Pipeline instance used by this step.
    """

    chunks = search_pipeline.run({
        "query_embedder": {"text": query.query},
        "retriever": {
            "top_k": query.top_k,
        }
    })["context_extractor"]["contexts"]

    return chunks


def query_elicitation_pipeline():
    """
    Execute query elicitation pipeline.
    """
    return pipeline_constructor(
        tmpl.QUESTION_ELICITATION_TEMPLATE,
        required_variables=["dialog", "lang"],
        generation_kwargs={}
    )


def extracted_data_correction_pipeline():
    """
    Execute extracted data correction pipeline.
    """
    return pipeline_constructor(
        tmpl.EXTRACTED_DATA_CORRECTION_PIPELINE,
        required_variables=["dialog", "extracted_json"],
        generation_kwargs={},
    )


def answer_formulation_pipeline():
    """
    Execute answer formulation pipeline.
    """
    return pipeline_constructor(
        tmpl.ANSWER_FORMULATION_TEMPLATE,
        required_variables=["search_query",
                            "search_intent", "contexts", "lang"],
        generation_kwargs={}
    )


def search_pipeline(document_store: PgvectorDocumentStore):
    """
    Search pipeline.

    :param document_store: Configured Haystack document store.
    """
    @component
    class ContextExtractor:

        def _get_context(self, given_chunk: Document, context_window: int) -> str:
            """
            Execute get context.
            """
            source_id = given_chunk.meta['source_id']
            filters = {
                "operator": "AND",
                "conditions": [
                    {"field": "meta.source_id", "operator": "==", "value": source_id}
                ]
            }

            all_related_chunks = sorted(
                document_store.filter_documents(filters=filters),
                key=lambda doc: doc.meta.get("split_idx_start", 0)
            )

            all_related_text_chunks = cast(list[str], [
                chunk.content for chunk in all_related_chunks
            ])

            given_chunk_idx = (
                0 if given_chunk.content is None else
                all_related_text_chunks.index(given_chunk.content))

            start_idx = max(0, given_chunk_idx - context_window)
            end_idx = min(len(all_related_text_chunks),
                          given_chunk_idx + context_window + 1)

            context = all_related_text_chunks[start_idx:end_idx]
            return ''.join(context) if context else ''

        @component.output_types(contexts=list[str])
        def run(self, chunks: list[Document], context_window: int = 2):
            contexts = []
            chunks_sorted = sorted(
                chunks,
                key=lambda x: x.score if x.score else 0.0, reverse=True
            )
            for given_chunk in chunks_sorted:
                context = self._get_context(given_chunk, context_window)
                contexts.append(context)

            return {"contexts": contexts}

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
    pipeline.add_component("context_extractor", ContextExtractor())

    pipeline.connect("query_embedder.embedding", "retriever.query_embedding")
    pipeline.connect("retriever.documents", "context_extractor.chunks")
    return pipeline


if __name__ == "__main__":
    from colorama import Fore
    messages = [
        ChatMessage.from_system(
            "You are a helpful assistant. Answer briefly."),
        ChatMessage.from_user("I cannot log in."),
        ChatMessage.from_assistant(
            "Could you share your email address?"),
        ChatMessage.from_user("My email is listed below."),
        ChatMessage.from_assistant("email?"),
        ChatMessage.from_user("a.n.borealis@gmail.com"),
        ChatMessage.from_assistant(
            "Thanks. What exact error do you see?"),
        ChatMessage.from_user("White screen after sign-in."),
        ChatMessage.from_assistant(
            "Is this in Chrome, Firefox, or Safari?"),
        ChatMessage.from_user("Chrome."),
        ChatMessage.from_assistant("Did you try incognito mode?"),
        ChatMessage.from_user("Yes")
    ]

    current_state = {
        'product': '',
        'payment_options': '',
        'technical_details': '',
        'email': 'a.n.borealis@gmail.com'
    }

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

    CHAT_SEARCH_PIPELINE = search_pipeline(DOCUMENT_STORE)
    QUESTION_ELICITATION_PIPELINE = query_elicitation_pipeline()
    EXTRACTED_DATA_CORRECTION_PIPELINE = extracted_data_correction_pipeline()
    ANSWER_FORMULATION_PIPELINE = answer_formulation_pipeline()

    def _process_inbox():
        """
        Process one inbox cycle in the interactive demo loop.

        :return: 1 when a search answer is produced, otherwise 0.
        """
        global current_state

        parsed_answer: dict[str, str]
        while True:
            result = QUESTION_ELICITATION_PIPELINE.run({
                "prompt": {
                    "dialog": serialize_chat_messages(messages),
                    "lang": "English"
                }
            }, include_outputs_from={"prompt"})
            raw_answer = result["llm"]["replies"][0]

            print(f"{Fore.WHITE}Raw search query JSON: <{raw_answer}>")

            try:
                parsed_answer = extract_json(raw_answer)
            except (ValueError, json.JSONDecodeError) as e:
                print(f"{Fore.RED}JSON parse error: {e}")
                continue

            if parsed_answer["action"] == "search":
                break

            messages.append(ChatMessage.from_assistant(
                parsed_answer["clarification_question"]))

            print(
                f'{Fore.WHITE}Clarification: {parsed_answer["clarification_question"]}')

            return 0

        print(f'{Fore.GREEN}SEARCH QUERY:{parsed_answer["search_query"]}')

        result = EXTRACTED_DATA_CORRECTION_PIPELINE.run({
            "prompt": {
                "dialog": serialize_chat_messages(messages),
                "extracted_json": current_state,
            }
        }, include_outputs_from={"prompt"}
        )

        prompt = result["prompt"]
        corrected_state_raw = result["llm"]["replies"][0]

        print(f"{Fore.CYAN}{prompt}")

        try:
            current_state = extract_json(corrected_state_raw)
        except (ValueError, json.JSONDecodeError):
            print(f"{Fore.RED}Error JSON extraction")
            pass

        print(f"{Fore.GREEN}CORRECTED STATE:", str(current_state))

        contexts = search_chunks(
            query=QueryContext(query=parsed_answer["search_query"], top_k=5),
            search_pipeline=CHAT_SEARCH_PIPELINE,
        )
        print(f"{Fore.BLUE}Retrieved contexts:")
        for c in contexts:
            print(c)

        final_result = ANSWER_FORMULATION_PIPELINE.run({
            "prompt": {
                "search_query": parsed_answer["search_query"],
                "search_intent": parsed_answer["search_intent"],
                "contexts": contexts,
                "lang": "english",
            }
        })

        print(f"{Fore.YELLOW}Final answer:",
              final_result["llm"]["replies"][0])
        return 1

    while True:
        flag = _process_inbox()
        # if flag == 1:
        #     break

        new_message = input(f"{Fore.WHITE}> ")
        if new_message in ["stop", "quit"]:
            break

        messages.append(ChatMessage.from_user(new_message))
