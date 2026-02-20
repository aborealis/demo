from haystack import Pipeline
from haystack.dataclasses import ChatMessage

from haystack_pipelines.helpers.templates import LANG_DETECTION_TEMPLATE
from haystack_pipelines.helpers.common import serialize_chat_messages, pipeline_constructor


def lang_detection() -> Pipeline:
    return pipeline_constructor(
        template=LANG_DETECTION_TEMPLATE,
        required_variables=["dialog"],
        generation_kwargs={
            "temperature": 0.0,         # Restrict sampling diversity for stable outputs.
            "top_p": 0.1,  # Restrict sampling diversity with a low top-p value.
        }
    )


if __name__ == "__main__":
    messages = [
        ChatMessage.from_user("Hi there"),
    ]

    LANG_DETECTION_PIPELINE = lang_detection()

    result = LANG_DETECTION_PIPELINE.run({
        "prompt": {
            "dialog": serialize_chat_messages(messages)
        }
    })

    print(result["llm"]["replies"][0])
