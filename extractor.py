import json
import csv
from pathlib import Path

# Paths
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"
OUTPUT_CSV = OUTPUT_DIR / "conversations_flat.csv"

# Load the JSON
with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
    conversations = json.load(f)

def flatten_messages(mapping, parent_id=None, flat_list=None):
    """Recursively flatten messages into a list of dicts."""
    if flat_list is None:
        flat_list = []

    for node_id, node in mapping.items():
        # Skip the root node if it has no message
        if node.get("message") and node_id != "client-created-root":
            message = node["message"]
            # Extract the content (join parts if multiple)
            content = ""
            if message.get("content") and message["content"].get("parts"):
                parts = message.get("content", {}).get("parts", [])
                flat_parts = []
                for part in parts:
                    if isinstance(part, str):
                        flat_parts.append(part)
                    elif isinstance(part, dict) and "text" in part:
                        flat_parts.append(part["text"])
                content = "\n".join(flat_parts)
            flat_list.append({
                "node_id": node_id,
                "parent_id": parent_id,
                "role": message["author"].get("role"),
                "create_time": message.get("create_time"),
                "update_time": message.get("update_time"),
                "content": content
            })

        # Recurse into children
        children = node.get("children", [])
        for child_id in children:
            if child_id in mapping:
                flatten_messages({child_id: mapping[child_id]}, parent_id=node_id, flat_list=flat_list)
    
    return flat_list

# Prepare rows
all_rows = []
for convo in conversations:
    mapping = convo.get("mapping", {})
    title = convo.get("title", "Untitled Conversation")
    flat_messages = flatten_messages(mapping)
    for row in flat_messages:
        row["conversation_title"] = title
    all_rows.extend(flat_messages)

# Write to CSV
with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["conversation_title", "node_id", "parent_id", "role", "create_time", "update_time", "content"])
    writer.writeheader()
    writer.writerows(all_rows)

print(f"Flattened {len(all_rows)} messages into {OUTPUT_CSV}")