"""Markdown output generation for classified URLs."""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


def generate_markdown(classified_urls: list[dict[str, Any]], debug: bool = False) -> str:
    """
    Generate markdown content from classified URLs.

    Args:
        classified_urls: List of dicts with {url, category, title, confidence, reason}
        debug: If True, include confidence and reason as comments

    Returns:
        Markdown string
    """
    # Group by category
    by_category = defaultdict(list)
    for item in classified_urls:
        by_category[item["category"]].append(item)

    # Build markdown
    lines = [f"# Tab Sweep - {datetime.now().strftime('%Y-%m-%d')}", ""]

    for category in sorted(by_category.keys()):
        items = by_category[category]
        lines.append(f"## {category}")
        lines.append("")

        for item in items:
            title = item.get("title") or item["url"]
            url = item["url"]
            summary = item.get("summary", "")

            if debug:
                confidence = item.get("confidence", 0)
                reason = item.get("reason", "")
                lines.append(f"[[{title}]]({url}) - {summary} <!-- confidence: {confidence:.2f}, reason: {reason} -->")
            else:
                # Obsidian link format: [[title]] - summary
                lines.append(f"[[{title}]]({url}) - {summary}")

        lines.append("")

    return "\n".join(lines)


def write_session_file(vault_path: str, content: str) -> Path:
    """
    Write session content to vault.

    Args:
        vault_path: Path to Obsidian vault
        content: Markdown content to write

    Returns:
        Path to created file
    """
    vault = Path(vault_path).expanduser()
    sessions_dir = vault / "Sessions"

    # Create Sessions directory if needed
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    filename = f"{datetime.now().strftime('%Y-%m-%d')} Tab Sweep.md"
    file_path = sessions_dir / filename

    # Append if file exists, otherwise create
    if file_path.exists():
        with open(file_path, "a") as f:
            f.write("\n\n---\n\n")
            f.write(content)
    else:
        with open(file_path, "w") as f:
            f.write(content)

    return file_path
