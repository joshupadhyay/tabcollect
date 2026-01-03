"""Database operations for tracking processed URLs."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

DB_DIR = Path.home() / ".tabsweep"
DB_FILE = DB_DIR / "db.json"


def ensure_db_dir() -> None:
    """Ensure the database directory exists."""
    DB_DIR.mkdir(parents=True, exist_ok=True)


def load_db() -> dict[str, Any]:
    """Load database from file."""
    if not DB_FILE.exists():
        return {"urls": {}}

    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"urls": {}}


def save_db(db: dict[str, Any]) -> None:
    """Save database to file."""
    ensure_db_dir()
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


def check_duplicate(url: str) -> tuple[bool, str | None]:
    """
    Check if URL is a duplicate.

    Returns:
        (is_duplicate, original_date)
    """
    db = load_db()
    urls = db.get("urls", {})

    if url in urls:
        original_session = urls[url].get("session", "unknown date")
        return True, original_session

    return False, None


def add_url(url: str, category: str, session: str) -> None:
    """Add URL to database."""
    db = load_db()

    if "urls" not in db:
        db["urls"] = {}

    db["urls"][url] = {
        "category": category,
        "timestamp": datetime.now().isoformat(),
        "session": session
    }

    save_db(db)


def add_urls_batch(urls: list[tuple[str, str]], session: str) -> None:
    """
    Add multiple URLs to database in batch.

    Args:
        urls: List of (url, category) tuples
        session: Session date string (e.g., "2026-01-02")
    """
    db = load_db()

    if "urls" not in db:
        db["urls"] = {}

    timestamp = datetime.now().isoformat()
    for url, category in urls:
        db["urls"][url] = {
            "category": category,
            "timestamp": timestamp,
            "session": session
        }

    save_db(db)
