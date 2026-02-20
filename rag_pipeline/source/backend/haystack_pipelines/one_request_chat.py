import os
from haystack import Pipeline
from haystack.dataclasses import ChatMessage
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from project_settings import USE_OLLAMA
from haystack_pipelines.helpers.common import SafeComponent, CHAT_GENERATOR_BREAKER


def one_request_chat_pipeline() -> Pipeline:
    """
    Execute one request chat pipeline.
    """
    pipeline = Pipeline()

    generator = OllamaChatGenerator(
        model="deepseek-r1:latest",
        url=os.environ['OLLAMA_BASE_URL'],
        generation_kwargs={
            "temperature": 0.9,
        }
    ) if USE_OLLAMA else OpenAIChatGenerator(
        model="gpt-4o-mini",
        generation_kwargs={
            "temperature": 0.9,
        }
    )

    safe_generator = SafeComponent(generator, CHAT_GENERATOR_BREAKER)

    pipeline.add_component("llm", safe_generator)
    return pipeline


if __name__ == "__main__":
    result: ChatMessage = one_request_chat_pipeline().run(
        {
            "llm": {
                "messages": [ChatMessage.from_user("What is 2 + 2?")]
            }
        }
    )["llm"]["replies"][0]

    print(result.text)
    print(result.meta["usage"])
