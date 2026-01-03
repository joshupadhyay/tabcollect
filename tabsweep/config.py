"""Configuration management for TabSweep."""

import json
from pathlib import Path
from typing import Any

# Default configuration
DEFAULT_CONFIG = {
    "vault_path": "",
    "model": "claude-3-5-haiku-latest",  # Super cheap and fast for URL classification
    "categories": [
        {
            "name": "Job Applications",
            "description": "Job postings, company career pages, application portals"
        },
        {
            "name": "Interview Prep",
            "description": "Coding challenges, system design, interview practice"
        },
        {
            "name": "Learning & Tutorials",
            "description": "Documentation, courses, how-to guides"
        },
        {
            "name": "Tools & Resources",
            "description": "Developer tools, utilities, productivity apps"
        },
        {
            "name": "Articles & Blogs",
            "description": "Technical articles, blog posts, opinions"
        },
        {
            "name": "Reference",
            "description": "API docs, specifications, cheat sheets"
        },
        {
            "name": "Shopping & Products",
            "description": "E-commerce, product pages, wishlists"
        },
        {
            "name": "Social & Entertainment",
            "description": "Social media, videos, entertainment"
        },
        {
            "name": "Maybe",
            "description": "Low confidence classifications"
        },
        {
            "name": "Uncategorized",
            "description": "Fallback for unclear URLs"
        }
    ],
    "rules": [
        {
            "domains": ["greenhouse.io", "lever.co", "ashbyhq.com", "workday.com", "myworkdayjobs.com"],
            "category": "Job Applications"
        },
        {
            "domains": ["leetcode.com", "hackerrank.com", "pramp.com"],
            "category": "Interview Prep"
        },
        {
            "path_contains": ["system-design", "interview", "coding-challenge"],
            "category": "Interview Prep"
        }
    ]
}

CONFIG_DIR = Path.home() / ".tabsweep"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config_path() -> Path:
    """Get the path to the config file."""
    return CONFIG_FILE


def ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    """Load configuration from file, return default if not found."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG.copy()


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to file."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def init_config(vault_path: str) -> dict[str, Any]:
    """Initialize configuration with vault path."""
    config = DEFAULT_CONFIG.copy()
    config["vault_path"] = str(Path(vault_path).expanduser())
    save_config(config)
    return config


def config_exists() -> bool:
    """Check if config file exists."""
    return CONFIG_FILE.exists()
