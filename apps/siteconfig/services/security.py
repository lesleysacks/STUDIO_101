"""Allowlists for URLs, media paths, and CSS values coming from JSON."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlsplit

from django.conf import settings
from django.templatetags.static import static

from .errors import ConfigIssue

EMBED_HOSTS = frozenset(
    {
        "www.youtube.com",
        "youtube.com",
        "www.youtube-nocookie.com",
        "player.vimeo.com",
        "www.facebook.com",
        "player.twitch.tv",
    }
)

FONT_STACKS = {
    "cinzel": "'Cinzel', Georgia, serif",
    "syne": "'Syne', 'Cinzel', Georgia, serif",
    "inter": "'Inter', system-ui, sans-serif",
    "jakarta": "'Plus Jakarta Sans', system-ui, sans-serif",
    "system": "system-ui, sans-serif",
}

_CSS_FORBIDDEN = (";", "{", "}", "<", ">", "\\", "url(", "expression", "@import")


def is_safe_href(value: str) -> bool:
    """Accept a site-relative path or an http(s) URL without embedded credentials."""
    if not value or not isinstance(value, str):
        return False
    if value.startswith("/") and not value.startswith("//"):
        parts = value.split("/")
        return "\\" not in value and ".." not in parts and "\n" not in value and "\r" not in value
    parsed = urlsplit(value)
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.hostname)
        and parsed.username is None
        and parsed.password is None
        and "\\" not in value
    )


def is_external_href(value: str) -> bool:
    return urlsplit(value).scheme in {"http", "https"}


def safe_embed_url(value: str, *, allow_any_https_host: bool) -> str:
    """Return a safe iframe src, or an empty string when the URL is rejected."""
    if not value or not isinstance(value, str):
        return ""
    parsed = urlsplit(value.strip())
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host or parsed.username or parsed.password:
        return ""
    if host in {"localhost", "127.0.0.1", "0.0.0.0"} or host.endswith(".local"):
        return ""
    if not allow_any_https_host and host not in EMBED_HOSTS:
        return ""
    if any(token in value for token in ("<", ">", '"', "'", "\n", "\r")):
        return ""
    return value.strip()


def is_safe_media_ref(value: str) -> bool:
    """Static asset path under ASSETS/, with no traversal."""
    if value == "":
        return True
    if not isinstance(value, str) or value.startswith(("/", "\\")) or ".." in Path(value).parts:
        return False
    if "\\" in value or "://" in value:
        return False
    return value.startswith("ASSETS/")


def static_file(relative: str) -> Path | None:
    if not is_safe_media_ref(relative) or not relative:
        return None
    root = (Path(settings.BASE_DIR) / "static").resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    if candidate.is_file():
        return candidate
    return None


def public_static_url(relative: str) -> str:
    path = static_file(relative)
    if path is None:
        return ""
    url = static(relative)
    if any(token in url for token in ('"', "'", "(", ")", ";", "<", ">", "\\")):
        return ""
    return url


def css_background_url(url: str) -> str:
    if not url or any(token in url for token in ('"', "'", "(", ")", ";", "<", ">", "\\")):
        return ""
    return url


def assert_css_fragment(value: str, *, file: str, path: str) -> None:
    lowered = value.lower()
    if any(token in lowered for token in _CSS_FORBIDDEN):
        raise ValueError(str(ConfigIssue("error", file, path, "CSS value contains a forbidden token.")))


def contained_directory(root: Path, candidate: Path) -> Path:
    """Resolve ``candidate`` and require it to stay inside ``root``."""
    resolved_root = root.resolve()
    resolved = candidate.resolve()
    if resolved != resolved_root and os.path.commonpath([str(resolved_root), str(resolved)]) != str(resolved_root):
        raise ValueError(f"Path escapes the configuration root: {candidate}")
    return resolved
