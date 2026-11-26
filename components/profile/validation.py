"""Small, dependency-free validators for profile forms."""
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9][0-9\s\-()]{6,19}$")
URL_RE = re.compile(r"^https?://[^\s/]+\.[^\s]+$", re.I)


def normalize_url(value: str) -> str:
    value = (value or "").strip()
    return value if not value or value.lower().startswith(("http://", "https://")) else "https://" + value


def valid_url(value: str) -> bool:
    return bool(URL_RE.match(value))
