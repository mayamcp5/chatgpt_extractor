# parsing/load_export.py

import json
from pathlib import Path

def load_conversations(path_or_data):
    if isinstance(path_or_data, (str, Path)):
        with open(path_or_data, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Already loaded JSON object
        return path_or_data