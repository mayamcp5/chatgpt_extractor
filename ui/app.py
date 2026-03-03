import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import json
import zipfile
import io
from datetime import datetime

from processing.build_view import build_conversation_view

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChatGPT Viewer",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Clean Sidebar CSS (No Overlay, No Hacks) ─────────────────────────────────
st.markdown("""
<style>

/* Sidebar header */
section[data-testid="stSidebar"] h2 {
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    margin: 4px 0 6px 0 !important;
}

/* Search input */
section[data-testid="stSidebar"] .stTextInput input {
    font-size: 0.85rem !important;
    border-radius: 6px !important;
}

/* Tight stacking */
section[data-testid="stSidebar"] div.stButton {
    margin: 0 !important;
    padding: 0 !important;
}

section[data-testid="stSidebar"] .element-container {
    margin-bottom: 4px !important;
}

/* Base sidebar button */
section[data-testid="stSidebar"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;

    text-align: left !important;
    white-space: normal !important;

    padding: 8px 12px !important;
    border-radius: 8px !important;

    font-size: 0.87rem !important;
    line-height: 1.15 !important;

    height: 60px !important;          /* 🔥 fixed height */
    display: flex !important;         /* 🔥 vertical layout control */
    flex-direction: column !important;
    justify-content: center !important;
    align-items: flex-start !important;

    overflow: hidden !important;      /* 🔥 prevent overflow */
    transition: background 0.12s ease;
}

/* Title (first line) */
section[data-testid="stSidebar"] button span {
    width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Hover */
section[data-testid="stSidebar"] button:hover {
    background: rgba(128,128,128,0.15) !important;
}

/* Active state */
section[data-testid="stSidebar"] button[kind="primary"] {
    background: rgba(99,102,241,0.18) !important;
    border-left: 3px solid rgb(99,102,241) !important;
    color: inherit !important;
}
            
section[data-testid="stSidebar"] .convo-list-wrap [data-testid="stCaptionContainer"] {
    padding: 0 10px 4px 10px !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}
            
section[data-testid="stSidebar"] .convo-list-wrap [data-testid="stCaptionContainer"] p {
    font-size: 0.72rem !important;
    opacity: 0.5 !important;
    margin: 0 !important;
    color: inherit !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("conversations", None), ("selected_id", None), ("view", "home")]:
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────────
def load_conversations(raw_data):
    convos = [build_conversation_view(c) for c in raw_data]
    convos.sort(key=lambda c: c.get("update_time") or 0, reverse=True)
    return convos


def visible_messages(messages):
    return [m for m in messages if (m.get("content") or "").strip()]


def format_dt(ts):
    if not ts:
        return "—"
    try:
        return datetime.fromtimestamp(ts).strftime("%b %d, %Y %H:%M")
    except Exception:
        return "—"


def format_dt_short(ts):
    if not ts:
        return "—"
    try:
        return datetime.fromtimestamp(ts).strftime("%b %d, %Y")
    except Exception:
        return "—"


def go_to_convo(convo_id):
    st.session_state["selected_id"] = convo_id
    st.session_state["view"] = "conversation"
    st.rerun()


# ── Home ──────────────────────────────────────────────────────────────────────
def show_home():
    st.title("ChatGPT Conversation Viewer")
    st.write("Upload your ChatGPT export to get started.")
    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Option 1 — `conversations.json`")
        json_file = st.file_uploader(
            "Select conversations.json", type=["json"], key="json_upload"
        )
        if json_file:
            raw = json.load(json_file)
            st.session_state["conversations"] = load_conversations(raw)
            go_to_convo(st.session_state["conversations"][0]["conversation_id"])

    with col2:
        st.markdown("#### Option 2 — ChatGPT export `.zip`")
        zip_file = st.file_uploader(
            "Select ChatGPT export ZIP", type=["zip"], key="zip_upload"
        )
        if zip_file:
            with zipfile.ZipFile(io.BytesIO(zip_file.read())) as z:
                match = next(
                    (n for n in z.namelist() if n.endswith("conversations.json")),
                    None,
                )
                if match:
                    with z.open(match) as f:
                        raw = json.load(f)
                    st.session_state["conversations"] = load_conversations(raw)
                    go_to_convo(st.session_state["conversations"][0]["conversation_id"])

    default_path = Path("data/conversations.json")
    if default_path.exists():
        st.markdown("---")
        if st.button("Load data/conversations.json"):
            with open(default_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            st.session_state["conversations"] = load_conversations(raw)
            go_to_convo(st.session_state["conversations"][0]["conversation_id"])


# ── Overview ───────────────────────────────────────────────────────────────────
def show_overview(conversations):
    st.title("Conversations Overview")

    all_msgs = [
        m
        for c in conversations
        for m in visible_messages(c.get("messages", []))
    ]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Conversations", len(conversations))
    c2.metric("Total Messages", len(all_msgs))
    c3.metric("Total Words", sum(m.get("word_count", 0) for m in all_msgs))

    st.markdown("---")

    for c in conversations:
        msgs = visible_messages(c.get("messages", []))
        title = c.get("title") or "Untitled"
        last_updated = format_dt_short(c.get("update_time"))

        with st.expander(f"**{title}** · {last_updated} · {len(msgs)} messages"):
            st.markdown(f"- Messages: {len(msgs)}")
            st.markdown(f"- Words: {sum(m.get('word_count', 0) for m in msgs)}")
            if st.button("View conversation", key=f"goto_{c['conversation_id']}"):
                go_to_convo(c["conversation_id"])


# ── Conversation View ─────────────────────────────────────────────────────────
def show_conversation(conversations):
    selected_id = st.session_state["selected_id"]
    selected = next(
        (c for c in conversations if c["conversation_id"] == selected_id),
        conversations[0],
    )

    msgs = visible_messages(selected.get("messages", []))

    st.title(selected["title"])
    if selected.get("update_time"):
        st.caption(f"Last updated: {format_dt(selected['update_time'])}")

    c1, c2 = st.columns(2)
    c1.metric("Messages", len(msgs))
    c2.metric("Total Words", sum(m.get("word_count", 0) for m in msgs))

    st.markdown("---")

    for msg in msgs:
        role = "user" if msg.get("is_user", False) else "assistant"
        label = "User" if role == "user" else "ChatGPT"

        with st.chat_message(role):
            st.markdown(msg["content"])
            st.caption(
                f"{label} · {format_dt(msg.get('create_time'))} · {msg.get('word_count', 0)} words"
            )


# ── Sidebar ────────────────────────────────────────────────────────────────────
def show_sidebar(conversations):
    with st.sidebar:
        st.markdown("## Conversations")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Home", use_container_width=True):
                st.session_state["view"] = "home"
                st.rerun()
        with col2:
            if st.button("Overview", use_container_width=True):
                st.session_state["view"] = "overview"
                st.rerun()

        st.markdown("---")

        search = st.text_input("Search", placeholder="Filter conversations...")

        filtered = (
            [c for c in conversations if search.lower() in (c.get("title") or "").lower()]
            if search
            else conversations
        )

        current_id = st.session_state.get("selected_id")

        for convo in filtered:
            cid = convo["conversation_id"]
            title = convo.get("title") or "Untitled"
            msgs = visible_messages(convo.get("messages", []))
            last_updated = format_dt_short(convo.get("update_time"))

            short_title = title[:40] + ("..." if len(title) > 40 else "")

            # Title (normal weight) + meta (lighter tone)
            label = (
                f"{short_title}\n"
                f"  {last_updated} · {len(msgs)} messages"
            )

            if st.button(
                f"**{short_title}**  \n{last_updated} · {len(msgs)} messages",
                key=f"sb_{cid}",
                use_container_width=True,
                type="primary" if cid == current_id else "secondary",
            ):
                go_to_convo(cid)


# ── Router ─────────────────────────────────────────────────────────────────────
conversations = st.session_state.get("conversations")

if conversations is None:
    show_home()
else:
    show_sidebar(conversations)
    view = st.session_state.get("view", "conversation")

    if view == "home":
        show_home()
    elif view == "overview":
        show_overview(conversations)
    else:
        show_conversation(conversations)