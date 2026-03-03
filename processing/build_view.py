from parsing.flatten_tree import flatten_conversation
from processing.normalize import normalize_messages
from processing.summary import build_conversation_summary


def build_conversation_view(convo):
    from parsing.flatten_tree import flatten_conversation
    from processing.normalize import normalize_messages
    from processing.summary import build_conversation_summary

    flat = flatten_conversation(convo)
    normalized = normalize_messages(flat)
    summary = build_conversation_summary(normalized)

    title = convo.get("title", "")
    if "screen time" in title.lower() and "steps" in title.lower():
        print(f"\n=== AFTER flatten_conversation ===")
        for m in flat:
            print(f"  {m['role']:12} ts={m['create_time']}  content={repr(m['content'][:40]) if m['content'] else repr('')}")
        
        print(f"\n=== AFTER normalize_messages ===")
        for m in normalized:
            print(f"  turn={m['turn_index']}  {m['role']:12} ts={m['create_time']}  content={repr(m['content'][:40]) if m['content'] else repr('')}")

    return {
        "conversation_id": convo.get("id"),
        "title": convo.get("title") or "Untitled Conversation",
        "update_time": convo.get("update_time"),
        "messages": normalized,
        "summary": summary,
    }