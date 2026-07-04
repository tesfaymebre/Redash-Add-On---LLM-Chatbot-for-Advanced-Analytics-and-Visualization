from quart import Blueprint, jsonify, request

from redash_chatbot.services.chat_service import process_chat

chat_bp = Blueprint("chat", __name__)


@chat_bp.post("/api/chat")
async def chat():
    """
    Main chat endpoint for the Redash add-on.

    Accepts natural language questions plus optional Redash context.
    Returns answer (+ SQL in Task 4).
    """
    body = await request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()

    if not question:
        return jsonify({"error": "question is required"}), 400

    context = body.get("context")
    session_id = body.get("session_id")

    result = process_chat(question=question, context=context, session_id=session_id)
    return jsonify(result), 200
