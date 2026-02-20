import os
import re
import json
from typing import Any, Mapping
from datetime import timedelta

from aiobreaker import CircuitBreaker
from haystack import Pipeline
from haystack.dataclasses import ChatMessage
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack_integrations.components.generators.ollama import OllamaGenerator
from haystack.components.generators import OpenAIGenerator
from project_settings import USE_OLLAMA


DOCS_EMBEDDING_BREAKER = CircuitBreaker(
    name="doc_embedding",
    fail_max=4,
    timeout_duration=timedelta(seconds=60),
)

TEXT_EMBEDDING_BREAKER = CircuitBreaker(
    name="txt_embedding",
    fail_max=4,
    timeout_duration=timedelta(seconds=60),
)

CHAT_GENERATOR_BREAKER = CircuitBreaker(
    name="LLM_chat",
    fail_max=4,
    timeout_duration=timedelta(seconds=60),
)

GENERATOR_BREAKER = CircuitBreaker(
    name="LLM_generator",
    fail_max=4,
    timeout_duration=timedelta(seconds=60),
)


class SafeComponent:

    def __init__(self, component_instance: Any, breaker: CircuitBreaker):
        self._component = component_instance
        self._breaker = breaker

        if hasattr(component_instance, "__haystack_input__"):
            self.__haystack_input__ = component_instance.__haystack_input__
        if hasattr(component_instance, "__haystack_output__"):
            self.__haystack_output__ = component_instance.__haystack_output__

    def run(self, *args: Any, **kwargs: Any) -> Mapping[str, Any]:
        """
        Execute run.
        """
        return self._breaker.call(self._component.run, *args, **kwargs)

    def __getattr__(self, item: str) -> Any:
        return getattr(self._component, item)


def serialize_chat_messages(messages: list[ChatMessage]) -> str:
    """
    Serialize chat messages.

    :param messages: Input collection for processing.
    """
    message_texts = [{m.role: m.text} for m in messages]
    return json.dumps(message_texts, ensure_ascii=False, indent=2)


def extract_json(text: str) -> dict:
    match = re.search(r'\{.*\}', text, re.S)
    if not match:
        raise ValueError("JSON not found in model output")
    return json.loads(match.group())


def pipeline_constructor(template: str,
                         required_variables: list,
                         generation_kwargs: dict,
                         ):

    llm = OllamaGenerator(
        model="deepseek-r1:latest",
        url=os.environ['OLLAMA_BASE_URL'],
        generation_kwargs=generation_kwargs,
    ) if USE_OLLAMA else OpenAIGenerator(
        model="gpt-4o-mini",
        generation_kwargs=generation_kwargs,
    )

    safe_llm = SafeComponent(llm, GENERATOR_BREAKER)

    pipeline = Pipeline()
    pipeline.add_component("prompt", PromptBuilder(
        template=template,
        required_variables=required_variables
    ))
    pipeline.add_component("llm", safe_llm)
    pipeline.connect("prompt", "llm")

    return pipeline
