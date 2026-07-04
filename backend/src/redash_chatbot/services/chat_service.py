"""
Chat business logic.

Step 3a: stub responses that validate the API contract.
Task 4: replace with LangChain SQL agent + OpenAI.
"""

from __future__ import annotations

import uuid
from typing import Any


def process_chat(
    question: str,
    context: dict[str, Any] | None,
    session_id: str | None,
) -> dict[str, Any]:
    """
    Handle a chat request and return a structured response.

    Args:
        question: Natural language user input.
        context: Optional Redash context (query editor, dashboard widget).
        session_id: Optional conversation id for multi-turn (Task 4).
    """
    context = context or {}
    context_type = context.get("type", "query_editor")
    sid = session_id or str(uuid.uuid4())

    if context_type == "dashboard_widget":
        query_name = context.get("query_name") or "this widget"
        viz = context.get("visualization_name") or context.get("visualization_type") or "chart"
        preview = context.get("result_preview")
        preview_note = ""
        if preview and isinstance(preview, dict):
            total = preview.get("total_rows", 0)
            preview_note = f" Received {total} result row(s) for context."
        answer = (
            f'Looking at widget "{query_name}" ({viz}).{preview_note} '
            f'Your question: "{question.strip()}". '
            "Summarization and insight extraction will be enabled in Task 4."
        )
        route = "stub_dashboard"
    else:
        answer = (
            f'Received your question: "{question.strip()}". '
            f"Context: {context_type}. "
            "SQL generation and insight extraction will be enabled in Task 4."
        )
        route = "stub"

    return {
        "answer": answer,
        "sql": None,
        "route": route,
        "session_id": sid,
    }
