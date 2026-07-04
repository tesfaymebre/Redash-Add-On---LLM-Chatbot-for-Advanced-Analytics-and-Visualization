from quart import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
async def health():
    """Liveness probe for Docker and CI."""
    return jsonify({"status": "ok", "service": "redash-chatbot-backend"}), 200
