# parsing/flatten_tree.py


def extract_content(message):
    content = ""
    if message.get("content") and message["content"].get("parts"):
        parts = message["content"]["parts"]
        flat_parts = []
        for part in parts:
            if isinstance(part, str):
                flat_parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                flat_parts.append(part["text"])
        content = "\n".join(flat_parts)
    return content


def flatten_conversation(convo):
    """
    Reconstruct the conversation in correct logical order by walking the
    parent->child chain from root to the deepest leaf.

    Why not DFS on children[]:
      ChatGPT stores edited/regenerated messages as sibling branches. The
      children[] array may contain multiple nodes (alternate versions), and
      their list order does not reflect temporal or logical sequence. The
      timestamps are also unreliable — the assistant reply is sometimes
      assigned an earlier timestamp than the user message that prompted it.

    The correct approach: find the trunk of the conversation tree by always
    following the LAST child at each node (the most recent/active branch),
    building an ordered list from root to leaf.
    """
    mapping = convo.get("mapping", {})

    # Find the root node (no parent)
    root_id = next(
        (k for k, v in mapping.items() if v.get("parent") is None), None
    )
    if not root_id:
        return []

    # Walk root -> leaf, always picking the last child (active branch)
    ordered_ids = []
    current_id = root_id
    while current_id:
        ordered_ids.append(current_id)
        children = mapping.get(current_id, {}).get("children", [])
        current_id = children[-1] if children else None

    # Build flat list from the ordered node IDs
    flat_list = []
    for node_id in ordered_ids:
        if node_id == "client-created-root":
            continue
        node = mapping.get(node_id)
        if not node:
            continue
        message = node.get("message")
        if not message:
            continue

        flat_list.append({
            "conversation_id": convo.get("id"),
            "conversation_title": convo.get("title"),
            "node_id": node_id,
            "parent_id": node.get("parent"),
            "role": message["author"].get("role"),
            "create_time": message.get("create_time"),
            "update_time": message.get("update_time"),
            "content": extract_content(message),
        })

    return flat_list