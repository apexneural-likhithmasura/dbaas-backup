#!/usr/bin/env python3
"""
List tables in the configured PostgreSQL schema.

Uses the project's existing DatabaseManager and settings.
"""

import sys
from pathlib import Path
import json

# Ensure project root on path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.database import db_manager  # noqa: E402
from app.core.config import settings  # noqa: E402


def main() -> None:
    schema = settings.db_schema
    result = {"schema": schema, "tables": []}
    try:
        with db_manager.get_cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                ORDER BY table_name
                """,
                (schema,),
            )
            rows = cur.fetchall()
            result["tables"] = [r["table_name"] for r in rows]
    except Exception as e:  # pragma: no cover
        result = {"error": str(e)}

    print(json.dumps(result))


if __name__ == "__main__":
    main()


