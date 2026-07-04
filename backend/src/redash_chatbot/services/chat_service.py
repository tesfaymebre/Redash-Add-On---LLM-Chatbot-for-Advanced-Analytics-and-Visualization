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

    # Step 3a stub — proves routing works; Task 4 adds real NL→SQL
    answer = (
        f"Received your question: \"{question.strip()}\". "
        f"Context: {context_type}. "
        "SQL generation and insight extraction will be enabled in Task 4."
    )

    return {
        "answer": answer,
        "sql": None,
        "route": "stub",
        "session_id": sid,
    }
