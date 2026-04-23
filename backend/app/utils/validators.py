"""
Input validation utilities for VeriClip AI.
Pydantic validators and sports ontology checks.
"""

from typing import Optional
from pydantic import HttpUrl


def validate_sports_ontology(query: str) -> bool:
    """
    Check if a search query relates to sports content.

    Args:
        query: Search query string

    Returns:
        True if query matches sports ontology patterns
    """
    sports_keywords = [
        "cricket", "ipl", "football", "soccer", "tennis",
        "basketball", "hockey", "baseball", "rugby",
        "live stream", "highlights", "match", "tournament",
        "bcci", "fifa", "nba", "nfl",
    ]
    query_lower = query.lower()
    return any(kw in query_lower for kw in sports_keywords)


def validate_url_scheme(url: str) -> bool:
    """
    Validate that a URL uses an allowed scheme.

    Args:
        url: URL string to validate

    Returns:
        True if URL uses http or https
    """
    return url.startswith(("http://", "https://"))
