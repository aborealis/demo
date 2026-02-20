# import os
from haystack import Pipeline
from haystack_pipelines.helpers.templates import TRANSLATE_TEMPLATE
from haystack_pipelines.helpers.common import pipeline_constructor


def translate_pipeline() -> Pipeline:
    return pipeline_constructor(
        template=TRANSLATE_TEMPLATE,
        required_variables=["lang", "message"],
        generation_kwargs={
            "temperature": 0.5,
        },
    )


if __name__ == "__main__":
    TRANSLATION_PIPELINE = translate_pipeline()
    translation = TRANSLATION_PIPELINE.run({
        "prompt": {
            "lang": "English",
            "message": "Hello, how are you?"
        }
    })["llm"]["replies"][0]

    print(translation)
