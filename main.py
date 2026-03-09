from pathlib import Path
import csv
from datetime import datetime

from parsing.load_export import load_conversations
from parsing.flatten_tree import flatten_conversation
from processing.normalize import normalize_messages

DATA_PATH = Path("data/conversations.json")
OUTPUT_PATH = Path("output/conversations_flat.csv")

# Load conversations
conversations = load_conversations(DATA_PATH)

all_rows = []
for simple_id, convo in enumerate(conversations, start=1):
    convo_id = convo.get("id") or convo.get("conversation_id")
    title = convo.get("title", "Untitled Conversation")

    # Flatten & normalize
    flat = flatten_conversation(convo)
    normalized = normalize_messages(flat)

    # Filter out empty messages first
    nonempty_messages = [m for m in normalized if m.get("content")]

    for idx, msg in enumerate(nonempty_messages, start=1):
        content = msg["content"]
        role = "User" if msg.get("is_user") else "AI"

        # Format date/time nicely
        dt_readable = "—"
        if msg.get("create_time_readable"):
            try:
                dt = datetime.fromisoformat(msg["create_time_readable"])
                dt_readable = dt.strftime("%b %d, %Y %H:%M")
            except Exception:
                dt_readable = msg["create_time_readable"]

        all_rows.append({
            "conversation_id": convo_id,
            "conversation_simple_id": simple_id,
            "conversation_title": title,
            "role": role,
            "message_index": idx,  # now aligns correctly
            "datetime": dt_readable,
            "message": content
        })

# Write CSV
fieldnames = [
    "conversation_id",
    "conversation_simple_id",
    "conversation_title",
    "role",
    "message_index",
    "datetime",
    "message"
]

OUTPUT_PATH.parent.mkdir(exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_rows)

print(f"Exported {len(all_rows)} messages to {OUTPUT_PATH}")