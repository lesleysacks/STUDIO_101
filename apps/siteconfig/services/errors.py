"""Actionable configuration errors."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfigIssue:
    """One validation finding. ``file`` is relative to the configuration root."""

    level: str
    file: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.file}: {self.path}: {self.message}"


class ConfigError(Exception):
    """Raised when one or more configuration files are unsafe to publish."""

    def __init__(self, issues: list[ConfigIssue]):
        self.issues = issues
        super().__init__("\n".join(str(issue) for issue in issues))
