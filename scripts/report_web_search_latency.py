from __future__ import annotations

import argparse
import math
import os
import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote


def _percentile(values: list[int], percentile: int) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(percentile / 100 * len(ordered)) - 1)
    return ordered[index]


def _read_metrics(path: Path) -> tuple[list[int], list[int], int, int]:
    uri = f"file:{quote(str(path.resolve()))}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        rows = connection.execute(
            """
            SELECT search_status, search_latency_ms, total_latency_ms
            FROM attempts
            """
        ).fetchall()
    total_latencies = [row[2] for row in rows if isinstance(row[2], int) and row[2] >= 0]
    search_latencies = [
        row[1]
        for row in rows
        if row[0] in {"used", "failed"}
        and isinstance(row[1], int)
        and row[1] >= 0
    ]
    searched = sum(1 for row in rows if row[0] in {"used", "failed"})
    return total_latencies, search_latencies, searched, len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print aggregate search and end-to-end latency from the local QA journal."
    )
    parser.add_argument(
        "--journal",
        type=Path,
        default=Path(os.environ.get("JOURNAL_PATH", "var/qa-journal.sqlite3")),
    )
    args = parser.parse_args()
    try:
        total, search, searched, attempts = _read_metrics(args.journal)
    except (OSError, sqlite3.Error):
        print("journal_unavailable", file=sys.stderr)
        return 2

    share = (searched / attempts * 100) if attempts else 0.0
    print(f"attempts={attempts}")
    print(f"search_use_share_percent={share:.1f}")
    print(f"end_to_end_p50_ms={_percentile(total, 50)}")
    print(f"end_to_end_p95_ms={_percentile(total, 95)}")
    print(f"search_p50_ms={_percentile(search, 50)}")
    print(f"search_p95_ms={_percentile(search, 95)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
