from datetime import datetime

def build_conversation_summary(messages):
    """
    Build summary statistics for a conversation.
    """
    user_msgs = [m for m in messages if m.get("is_user")]
    assistant_msgs = [m for m in messages if m.get("is_assistant")]

    total_messages = len(messages)
    total_user_words = sum(m.get("word_count", 0) for m in user_msgs)
    total_assistant_words = sum(m.get("word_count", 0) for m in assistant_msgs)

    # Convert ISO strings to datetime objects
    times = []
    for m in messages:
        ts = m.get("create_time_readable")
        if ts:
            try:
                times.append(datetime.fromisoformat(ts))
            except Exception:
                pass

    # Compute duration in minutes
    duration_minutes = None
    if times:
        duration_minutes = (max(times) - min(times)).total_seconds() / 60

    # Compute average words per user message
    avg_user_words = (total_user_words / len(user_msgs)) if user_msgs else 0

    return {
        "total_messages": total_messages,
        "user_messages": len(user_msgs),
        "assistant_messages": len(assistant_msgs),
        "total_user_words": total_user_words,
        "total_assistant_words": total_assistant_words,
        "avg_user_words": avg_user_words,
        "conversation_duration_minutes": duration_minutes,
    }