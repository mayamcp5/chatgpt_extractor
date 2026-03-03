# processing/normalize.py

from datetime import datetime


def normalize_messages(messages):
    # Do NOT sort by timestamp. The tree walk in flatten_conversation()
    # traverses parent->children in the correct logical order. ChatGPT
    # sometimes assigns the assistant reply a slightly earlier timestamp
    # than the user message that prompted it, so any timestamp-based sort
    # will invert the order. Trust the tree-walk order as ground truth.

    for i, m in enumerate(messages):
        timestamp = m.get("create_time")

        # Turn index
        m["turn_index"] = i

        # Human-readable time
        if timestamp:
            dt = datetime.fromtimestamp(timestamp)
            m["create_time_readable"] = dt.isoformat()
            m["hour_of_day"] = dt.hour
        else:
            m["create_time_readable"] = None
            m["hour_of_day"] = None

        # Behavioral metrics
        content = m.get("content") or ""
        m["char_count"] = len(content)
        m["word_count"] = len(content.split())

        # Role flags
        m["is_user"] = m["role"] == "user"
        m["is_assistant"] = m["role"] == "assistant"

    return messages