# Scripts

ETL and automation utilities for loading `Data/` CSV exports into the analytics database.

Use the **root** `.venv` (not a separate env here):

```bash
make install
make profile-data
```

| Script | Purpose |
|--------|---------|
| `profile_data.py` | Profile raw CSVs → `docs/architecture/data-profile.txt` |
| `load_youtube_data.py` | Ingest CSVs into PostgreSQL (`make db-load`) |
| `youtube_config.py` | Shared folder→report_type mappings and parsers |

Dependencies: `scripts/requirements.txt` (installed via root `requirements.txt`).
