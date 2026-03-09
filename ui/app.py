import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
from pathlib import Path
import json
import io
import csv
from datetime import datetime

from parsing.load_export import load_conversations
from parsing.flatten_tree import flatten_conversation
from processing.normalize import normalize_messages

st.title("ChatGPT Export → CSV Converter")

# -----------------------------
# Upload section
# -----------------------------
mode = st.radio("Upload mode", ["Single file", "Multiple files"])

uploaded_files = None
if mode == "Single file":
    uploaded_file = st.file_uploader(
        "Upload a ChatGPT export JSON file",
        type="json",
        key="single_upload"
    )
    if uploaded_file:
        uploaded_files = [uploaded_file]
else:
    uploaded_files = st.file_uploader(
        "Upload ChatGPT export JSON files",
        type="json",
        accept_multiple_files=True,
        key="multi_upload"
    )

# -----------------------------
# Submit button
# -----------------------------
if st.button("Submit") and uploaded_files:
    for file_idx, uploaded_file in enumerate(uploaded_files, start=1):
        try:
            raw_data = json.load(uploaded_file)
        except Exception as e:
            st.error(f"Failed to read {uploaded_file.name}: {e}")
            continue

        # Load conversations
        conversations = load_conversations(raw_data)

        # Prepare one CSV per uploaded file
        all_rows = []

        for simple_id, convo in enumerate(conversations, start=1):
            convo_id = convo.get("id") or convo.get("conversation_id")
            title = convo.get("title", "Untitled Conversation")

            # Flatten & normalize
            flat = flatten_conversation(convo)
            normalized = normalize_messages(flat)
            nonempty_msgs = [m for m in normalized if m.get("content")]

            for idx, msg in enumerate(nonempty_msgs, start=1):
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
                    "role": "User" if msg.get("is_user") else "AI",
                    "message_index": idx,
                    "datetime": dt_readable,
                    "message": msg["content"]
                })

        # Write CSV to memory for the entire uploaded file
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "conversation_id",
                "conversation_simple_id",
                "conversation_title",
                "role",
                "message_index",
                "datetime",
                "message"
            ]
        )
        writer.writeheader()
        writer.writerows(all_rows)

        # Reset pointer
        output.seek(0)

        # One download button per uploaded file
        st.download_button(
            label=f"Download CSV: {uploaded_file.name}",
            data=output.getvalue(),
            file_name=f"{uploaded_file.name}.csv",
            mime="text/csv",
            key=f"download_{file_idx}"
        )