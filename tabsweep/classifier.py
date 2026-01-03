"""URL classification using rules and LLM."""

import json
import os
from typing import Any
from urllib.parse import urlparse

from anthropic import Anthropic


def classify_by_rules(url: str, rules: list[dict[str, Any]]) -> str | None:
    """
    Classify URL using domain and path rules.

    Args:
        url: The URL to classify
        rules: List of classification rules

    Returns:
        Category name or None if no rule matches
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    for rule in rules:
        # Check domain matches
        if "domains" in rule:
            for rule_domain in rule["domains"]:
                if domain == rule_domain or domain.endswith("." + rule_domain):
                    return rule["category"]

        # Check path contains keywords
        if "path_contains" in rule:
            for keyword in rule["path_contains"]:
                if keyword.lower() in path:
                    return rule["category"]

    return None


def classify_batch_with_llm(
    urls_data: list[dict[str, str | None]],
    categories: list[dict[str, str]],
    model: str = "claude-3-5-haiku-latest"
) -> list[dict[str, Any]]:
    """
    Classify a batch of URLs using Anthropic LLM.

    Args:
        urls_data: List of dicts with {url, title, description}
        categories: List of category definitions
        model: Anthropic model to use

    Returns:
        List of classification results with {category, confidence, reason, title}
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        # Fallback to Uncategorized if no API key
        return [
            {
                "category": "Uncategorized",
                "confidence": 0.0,
                "reason": "No API key configured",
                "title": data.get("title") or data["url"]
            }
            for data in urls_data
        ]

    client = Anthropic(api_key=api_key)

    # Build category list
    category_list = "\n".join([
        f"- {cat['name']}: {cat['description']}"
        for cat in categories
    ])

    # Build URLs section
    urls_section = []
    for i, data in enumerate(urls_data, 1):
        title = data.get("title") or "(unavailable)"
        description = data.get("description") or "(unavailable)"
        urls_section.append(
            f"{i}. URL: {data['url']}\n"
            f"   Title: {title}\n"
            f"   Description: {description}"
        )

    prompt = f"""Classify these URLs into categories and generate a short summary for each. Return valid JSON array.

Available categories:
{category_list}

URLs to classify:
{chr(10).join(urls_section)}

Return JSON array with exactly this format:
[
  {{
    "category": "Category Name",
    "confidence": 0.85,
    "reason": "Brief explanation",
    "title": "Cleaned title (extract from page title or URL)",
    "summary": "One-sentence summary of what this link contains"
  }},
  ...
]

Choose the best category for each URL. Use "Uncategorized" if none fit well. Confidence should be between 0 and 1.
For the summary, write a concise one-sentence description of the link's content based on the title and description."""

    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract JSON from response
        content = response.content[0].text.strip()

        # Try to extract JSON if wrapped in markdown code blocks
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content

        results = json.loads(content)

        # Validate and apply confidence threshold
        validated_results = []
        for result in results:
            # Force to Uncategorized if confidence < 0.65
            if result.get("confidence", 0) < 0.65:
                result["category"] = "Uncategorized"

            validated_results.append(result)

        return validated_results

    except (json.JSONDecodeError, Exception) as e:
        # Fallback to Uncategorized on any error
        return [
            {
                "category": "Uncategorized",
                "confidence": 0.0,
                "reason": f"Classification failed: {str(e)[:50]}",
                "title": data.get("title") or data["url"]
            }
            for data in urls_data
        ]
