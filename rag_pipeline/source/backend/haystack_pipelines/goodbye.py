from haystack_pipelines.helpers.common import pipeline_constructor
from haystack_pipelines.helpers.templates import GOOFBYE_TEMPLATE


def goodbye_pipeline():
    """
    Execute goodbye pipeline.
    """
    return pipeline_constructor(
        template=GOOFBYE_TEMPLATE,
        required_variables=["messages", "lang"],
        generation_kwargs={
            "temperature": 0.5,
        }
    )


if __name__ == "__main__":
    messages = ["Hi", "Can you help me?", "Thanks, goodbye"]

    GOOFBYE_PIPELINE = goodbye_pipeline()

    result = GOOFBYE_PIPELINE.run({
        "prompt": {
            "messages": messages
        }
    })["llm"]["replies"][0]

    print(result)
