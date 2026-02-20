"""Module description."""
from typing import cast
from services.storage.chat_redis import RedisChatMemoryCelery


def extract_redis_content(sync_memory: RedisChatMemoryCelery):
    """Extract redis content."""
    keys = cast(list[str], sync_memory.redis.keys("chat:*"))
    if not keys:
        return {
            "messages": [],
            "summary": None,
            "msg_idx": None,
            "user_context": None,
            "inbox_messages": None,
        }

    messages = sync_memory.get_messages_for_tests()
    summary = sync_memory.get_summary()
    msg_idx = sync_memory.get_last_message_idx_for_tests()
    user_context = sync_memory.get_user_context()
    inbox_messages = sync_memory.read_inbox_for_tests()

    return {
        "messages": messages,
        "summary": summary,
        "msg_idx": msg_idx,
        "user_context": user_context.text if user_context else "",
        "inbox_messages": inbox_messages,
    }
