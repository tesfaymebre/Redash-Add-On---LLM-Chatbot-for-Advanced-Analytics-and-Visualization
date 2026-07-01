#!/usr/bin/env python3
"""
Task 2a — Profile raw YouTube CSV exports under Data/

Run from repo root:
    python scripts/profile_data.py
    python scripts/profile_data.py --data-dir Data --output docs/architecture/data-profile.txt
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

# Map Data/ folder names → database report_type slugs
REPORT_SLUGS: dict[str, str] = {
    "Viewership by Date": "viewership_daily",
    "Device type": "device_type",
    "Geography": "geography",
    "Cities": "cities",
    "Traffic source": "traffic_source",
    "Operating system": "operating_system",
    "Content type": "content_type",
    "Subscription status": "subscription_status",
    "Subscription source": "subscription_source",
    "New and returning viewers": "new_returning_viewers",
    "Sharing service": "sharing_service",
    "Subtitles and CC": "subtitles_cc",
    "Viewer age": "viewer_age",
    "Viewer gender": "viewer_gender",
}


def profile_csv(path: Path) -> dict:
    """Return basic stats for one CSV file."""
    df = pd.read_csv(path)
    return {
        "path": str(path),
        "rows": len(df),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": df.isnull().sum().to_dict(),
        "sample_head": df.head(3).to_dict(orient="records"),
    }


def profile_data_dir(data_dir: Path) -> str:
    lines: list[str] = [
        "=" * 70,
        "YouTube Data/ Profile — Task 2a",
        f"Source: {data_dir.resolve()}",
        "=" * 70,
        "",
    ]

    for folder in sorted(data_dir.iterdir()):
        if not folder.is_dir():
            continue

        slug = REPORT_SLUGS.get(folder.name, folder.name.lower().replace(" ", "_"))
        lines.append(f"## {folder.name}  →  report_type: `{slug}`")
        lines.append("")

        for csv_file in sorted(folder.glob("*.csv")):
            stats = profile_csv(csv_file)
            lines.append(f"### {csv_file.name}")
            lines.append(f"- Rows: {stats['rows']}")
            lines.append(f"- Columns: {stats['columns']}")

            nulls = {k: v for k, v in stats["null_counts"].items() if v > 0}
            if nulls:
                lines.append(f"- Nulls: {nulls}")

            # Flag Total rollup row in Table data
            if csv_file.name == "Table data.csv" and stats["rows"] > 0:
                first_col = stats["columns"][0]
                df = pd.read_csv(csv_file)
                if str(df.iloc[0][first_col]).strip().lower() == "total":
                    lines.append("- Note: row 0 is a **Total** rollup (exclude on ETL load)")

            lines.append("")

        lines.append("")

    lines.append("=" * 70)
    lines.append("Schema DDL: infra/sql/001_init_schema.sql")
    lines.append("Design doc: docs/architecture/database-schema.md")
    lines.append("=" * 70)

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile YouTube CSV exports")
    parser.add_argument("--data-dir", type=Path, default=Path("Data"))
    parser.add_argument("--output", type=Path, default=None, help="Write report to file")
    args = parser.parse_args()

    report = profile_data_dir(args.data_dir)
    print(report)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"\nWrote profile to {args.output}")


if __name__ == "__main__":
    main()
