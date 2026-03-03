from pathlib import Path
import csv

from parsing.load_export import load_conversations
from parsing.flatten_tree import flatten_conversation
from processing.normalize import normalize_messages

DATA_PATH = Path("data/conversations.json")
OUTPUT_PATH = Path("output/conversations_flat.csv")

conversations = load_conversations(DATA_PATH)

all_rows = []
for convo in conversations:
    flat = flatten_conversation(convo)
    normalized = normalize_messages(flat)
    all_rows.extend(normalized)

with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
    writer.writeheader()
    writer.writerows(all_rows)