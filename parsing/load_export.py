# parsing/load_export.py

import json
from pathlib import Path

def load_conversations(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)