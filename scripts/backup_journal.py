from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def backup_journal(source: Path, destination: Path) -> Path:
    source = Path(source)
    destination = Path(destination)
    if not source.is_file():
        raise ValueError("journal_unavailable")
    if source.resolve() == destination.resolve() or destination.exists():
        raise ValueError("backup_destination_exists")

    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    destination.parent.chmod(0o700)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    temporary.chmod(0o600)
    try:
        with sqlite3.connect(source, timeout=10) as source_db:
            with sqlite3.connect(temporary) as destination_db:
                source_db.backup(destination_db)
        temporary.chmod(0o600)
        os.link(temporary, destination)
        temporary.unlink()
        return destination
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def main() -> int:
    source = Path(os.environ.get("JOURNAL_PATH", "var/journal.sqlite3"))
    backup_dir = Path(
        os.environ.get(
            "JOURNAL_BACKUP_DIR",
            str(source.parent / "backups"),
        )
    )
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = backup_dir / f"journal-{timestamp}.sqlite3"
    try:
        backup_journal(source, destination)
    except Exception:
        print("journal_backup: failed")
        return 1
    print(f"journal_backup: created {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
