import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import json
import io
import csv
import zipfile
from datetime import datetime

from parsing.load_export import load_conversations
from parsing.flatten_tree import flatten_conversation
from processing.normalize import normalize_messages


st.set_page_config(
    page_title="ChatGPT to CSV",
    page_icon="🗨️",
    layout="centered"
)

st.title("ChatGPT Export → CSV Converter")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Output Format <3")

st.sidebar.markdown(
"""
Each CSV row represents **one message** in a conversation.

**Columns**

• `conversation_id`  
Unique identifier from the ChatGPT export.

• `conversation_simple_id`  
Sequential ID for easier analysis.

• `conversation_title`  
Title of the conversation.

• `role`  
`User` or `AI`.

• `message_index`  
Order of the message within the conversation.

• `datetime`  
Timestamp converted to a readable format.

• `message`  
Text content of the message.
"""
)

# -----------------------------
# Upload Mode
# -----------------------------
mode = st.radio("Upload mode", ["Single file", "Multiple files (ZIP)"])

uploaded_files = []

if mode == "Single file":

    uploaded_file = st.file_uploader(
        "Upload a ChatGPT export conversations.JSON file",
        type="json"
    )

    if uploaded_file:
        uploaded_files = [uploaded_file]


else:

    zip_file = st.file_uploader(
        "Upload a ZIP containing multiple conversation.json files",
        type="zip"
    )

    if zip_file:

        with zipfile.ZipFile(zip_file) as z:

            for path in z.namelist():

                # Only process conversations.json
                if not path.endswith("conversations.json"):
                    continue

                data = io.BytesIO(z.read(path))

                path_obj = Path(path)

                # Determine participant name
                if path_obj.parent.name:
                    participant = path_obj.parent.name
                else:
                    participant = path_obj.stem

                data.name = f"{participant}_conversations.json"

                uploaded_files.append(data)

# -----------------------------
# Submit button
# -----------------------------
if st.button("Submit") and uploaded_files:

    csv_outputs = []
    used_names = set()

    for uploaded_file in uploaded_files:

        try:
            raw_data = json.load(uploaded_file)
        except Exception as e:
            st.error(f"Failed to read {uploaded_file.name}: {e}")
            continue

        conversations = load_conversations(raw_data)

        all_rows = []

        for simple_id, convo in enumerate(conversations, start=1):

            convo_id = convo.get("id") or convo.get("conversation_id")
            title = convo.get("title", "Untitled Conversation")

            flat = flatten_conversation(convo)
            normalized = normalize_messages(flat)

            nonempty_msgs = [m for m in normalized if m.get("content")]

            for idx, msg in enumerate(nonempty_msgs, start=1):

                dt_readable = "—"

                if msg.get("create_time_readable"):
                    try:
                        dt = datetime.fromisoformat(msg["create_time_readable"])
                        dt_readable = dt.strftime("%Y-%m-%d %H:%M")
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

        # Create CSV
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

        output.seek(0)

        # Clean participant name
        participant = Path(uploaded_file.name).stem.replace("_conversations", "")

        filename = f"{participant}.csv"

        # Prevent duplicate filenames
        counter = 2
        base = participant
        while filename in used_names:
            filename = f"{base}_{counter}.csv"
            counter += 1

        used_names.add(filename)

        csv_outputs.append((filename, output.getvalue()))

    st.success(f"Processed {len(csv_outputs)} export file(s).")

    # -----------------------------
    # Single CSV
    # -----------------------------
    if len(csv_outputs) == 1:

        filename, data = csv_outputs[0]

        st.download_button(
            label="Download CSV",
            data=data,
            file_name=filename,
            mime="text/csv"
        )

    # -----------------------------
    # Multiple → ZIP
    # -----------------------------
    else:

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as z:

            for filename, data in csv_outputs:
                z.writestr(filename, data)

        zip_buffer.seek(0)

        st.download_button(
            label="Download All CSVs (ZIP)",
            data=zip_buffer,
            file_name="chatgpt_csv_exports.zip",
            mime="application/zip"
        )