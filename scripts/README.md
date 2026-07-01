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
| `load_youtube_data.py` | *(Task 2b)* Ingest CSVs into PostgreSQL |

Dependencies: `scripts/requirements.txt` (installed via root `requirements.txt`).
