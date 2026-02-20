from haystack.dataclasses import ChatMessage
from haystack_pipelines.helpers.common import pipeline_constructor
from haystack_pipelines.helpers.templates import USER_CONTEXT_TEMPLATE


def user_context_pipeline():
    """
    Execute user context pipeline.
    """

    return pipeline_constructor(
        template=USER_CONTEXT_TEMPLATE,
        required_variables=["user_context", "messages"],
        generation_kwargs={
            "temperature": 0.0,
            "top_p": 0.1,
        }
    )


if __name__ == "__main__":
    messages = [
        ChatMessage.from_user("I need help with account access."),
        ChatMessage.from_assistant("Sure, could you share your email?"),
        ChatMessage.from_user("test@test.ru"),
        ChatMessage.from_assistant("Thanks, what issue do you see exactly?"),
        ChatMessage.from_user("I see a white screen."),
        ChatMessage.from_assistant("Please try another browser and disable VPN for a quick check."),
        ChatMessage.from_user("I tried that."),
        ChatMessage.from_assistant("Got it: browser check done, issue persists."),
        ChatMessage.from_user("Yes")
    ]

    USER_CONTEXT_PIPELINE = user_context_pipeline()
    result = USER_CONTEXT_PIPELINE.run({
        "prompt": {
            "user_context": "No profile facts saved yet.",
            "messages": [m.text for m in messages if m.role == "user"],
        }
    })

    print(result["llm"]["meta"][0]["thinking"])
    print(result["llm"]["replies"][0])
    print(result["llm"]["meta"][0]["usage"]["total_tokens"])
