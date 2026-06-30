# Backend — Redash Chatbot API

Async Quart service that will handle:

- Natural language → SQL translation
- Dashboard / visualization summarization
- Insight extraction over query results

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
hypercorn redash_chatbot.app:app --reload --bind 0.0.0.0:8000
```
