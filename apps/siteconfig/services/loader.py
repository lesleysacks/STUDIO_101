"""Load, validate, cache, and invalidate the site configuration bundle."""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from django.conf import settings

from .errors import ConfigError, ConfigIssue
from .registry import COMPONENTS
from .schema import apply_defaults, validate_schema
from .security import contained_directory, is_safe_href, is_safe_media_ref, static_file
from .theme import build_theme_css

logger = logging.getLogger("apps.siteconfig")

REQUIRED_FILES = ("site.json", "theme.json", "navigation.json")
_LOCK = threading.Lock()
_CACHE: dict[str, Any] = {"key": None, "bundle": None, "last_valid": None, "last_valid_root": None}


@dataclass
class SiteBundle:
    site: dict
    theme: dict
    theme_css: str
    navigation: dict
    pages: dict[str, dict]
    services: dict[str, dict]
    portfolio: dict[str, dict]
    warnings: list[ConfigIssue] = field(default_factory=list)


def config_root() -> Path:
    return Path(settings.SITECONFIG_ROOT)


def reset_cache() -> None:
    with _LOCK:
        _CACHE.update({"key": None, "bundle": None, "last_valid": None, "last_valid_root": None})


def _read_json(root: Path, relative: str) -> tuple[Any, list[ConfigIssue]]:
    issues: list[ConfigIssue] = []
    path = root / relative
    try:
        contained_directory(root, path)
    except ValueError:
        return None, [ConfigIssue("error", relative, "$", "File path escapes the configuration root.")]
    if not path.is_file():
        return None, [ConfigIssue("error", relative, "$", "File is missing.")]
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except UnicodeDecodeError:
        return None, [ConfigIssue("error", relative, "$", "File is not valid UTF-8.")]
    except json.JSONDecodeError as exc:
        return None, [ConfigIssue("error", relative, "$", f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}.")]
    if not isinstance(data, dict):
        issues.append(ConfigIssue("error", relative, "$", "The document must be a JSON object."))
    return data, issues


def _schema(root: Path, name: str) -> tuple[dict | None, list[ConfigIssue]]:
    relative = f"schemas/{name}" if not name.startswith("components/") else f"schemas/{name}"
    if name.endswith(".schema.json") and "/" not in name:
        relative = f"schemas/{name}"
    data, issues = _read_json(root, relative)
    return data, issues


def _component_schema_path(name: str) -> str:
    return f"components/{name}"


def _validate_document(root: Path, relative: str, schema_name: str) -> tuple[dict | None, list[ConfigIssue]]:
    schema, schema_issues = _schema(root, schema_name)
    data, data_issues = _read_json(root, relative)
    issues = schema_issues + data_issues
    if schema is None or data is None or issues:
        return None, issues
    issues.extend(validate_schema(schema, data, relative))
    if issues:
        return None, issues
    apply_defaults(schema, data)
    return data, []


def _merge_settings(site: dict, component_type: str, settings_data: dict) -> dict:
    merged: dict[str, Any] = {}
    defaults = (site.get("component_defaults") or {}).get(component_type) or {}
    if isinstance(defaults, dict):
        merged.update(defaults)
    merged.update(settings_data)
    return merged


def _check_href(file: str, path: str, value: str, issues: list[ConfigIssue]) -> None:
    if value and not is_safe_href(value):
        issues.append(ConfigIssue("error", file, path, "URL must be a site path or an http(s) URL."))


def _check_media(file: str, path: str, value: str, issues: list[ConfigIssue], warnings: list[ConfigIssue]) -> None:
    if not value:
        return
    if not is_safe_media_ref(value):
        issues.append(ConfigIssue("error", file, path, "Media path must stay inside ASSETS/ and cannot contain '..'."))
        return
    if static_file(value) is None:
        warnings.append(ConfigIssue("warning", file, path, "Media file was not found in static/."))


def _validate_sections(root: Path, page_file: str, page: dict, site: dict, issues: list[ConfigIssue], warnings: list[ConfigIssue]) -> None:
    seen: set[str] = set()
    for index, section in enumerate(page.get("sections", [])):
        section_path = f"$.sections[{index}]"
        section_id = section.get("id", "")
        if section_id in seen:
            issues.append(ConfigIssue("error", page_file, f"{section_path}.id", f"Duplicate section id {section_id!r}."))
        seen.add(section_id)
        component_type = section.get("type")
        component = COMPONENTS.get(component_type)
        if component is None:
            issues.append(ConfigIssue("error", page_file, f"{section_path}.type", f"Unknown component type {component_type!r}."))
            continue
        schema, schema_issues = _schema(root, _component_schema_path(component["schema"]))
        issues.extend(schema_issues)
        if schema is None:
            continue
        merged = _merge_settings(site, component_type, section.get("settings") or {})
        issues.extend(validate_schema(schema, merged, page_file, f"{section_path}.settings"))
        if not any(issue.path.startswith(f"{section_path}.settings") and issue.level == "error" for issue in issues):
            apply_defaults(schema, merged)
            section["settings"] = merged
        _walk_settings(page_file, f"{section_path}.settings", merged, issues, warnings)


def _walk_settings(file: str, path: str, value: Any, issues: list[ConfigIssue], warnings: list[ConfigIssue]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in {"href", "cta_href"} and isinstance(child, str):
                _check_href(file, child_path, child, issues)
            elif key in {"image", "featured_image"} and isinstance(child, str):
                _check_media(file, child_path, child, issues, warnings)
            elif key == "url" and isinstance(child, str) and child:
                from .security import safe_embed_url

                if safe_embed_url(child, allow_any_https_host=False) != child:
                    issues.append(ConfigIssue("error", file, child_path, "Video URL must be an https embed on an approved host."))
            else:
                _walk_settings(file, child_path, child, issues, warnings)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_settings(file, f"{path}[{index}]", child, issues, warnings)


def _load_collection(root: Path, folder: str, schema_name: str, issues: list[ConfigIssue], warnings: list[ConfigIssue]) -> dict[str, dict]:
    directory = root / folder
    if not directory.exists():
        return {}
    records: dict[str, dict] = {}
    for path in sorted(directory.glob("*.json")):
        relative = f"{folder}/{path.name}"
        schema, schema_issues = _schema(root, schema_name)
        data, data_issues = _read_json(root, relative)
        found = schema_issues + data_issues
        if schema is None or data is None:
            issues.extend(found)
            continue
        found.extend(validate_schema(schema, data, relative))
        if found:
            issues.extend(found)
            continue
        apply_defaults(schema, data)
        slug = data.get("slug", "")
        if slug in records:
            issues.append(ConfigIssue("error", relative, "$.slug", f"Duplicate slug {slug!r}."))
            continue
        if path.stem != slug:
            warnings.append(ConfigIssue("warning", relative, "$.slug", f"File name {path.stem!r} does not match slug {slug!r}."))
        _walk_settings(relative, "$", data, issues, warnings)
        records[slug] = data
    return records


def load_bundle(root: Path | None = None) -> SiteBundle:
    root = config_root() if root is None else root
    issues: list[ConfigIssue] = []
    warnings: list[ConfigIssue] = []
    documents: dict[str, dict] = {}
    for name in REQUIRED_FILES:
        schema_name = name.replace(".json", ".schema.json")
        data, found = _validate_document(root, name, schema_name)
        issues.extend(found)
        if data is not None:
            documents[name] = data
    if issues:
        raise ConfigError(issues)

    site = documents["site.json"]
    for component_type in site.get("component_defaults", {}):
        if component_type not in COMPONENTS:
            issues.append(ConfigIssue("error", "site.json", f"$.component_defaults.{component_type}", "Unknown component type."))

    pages: dict[str, dict] = {}
    pages_dir = root / "pages"
    if pages_dir.exists():
        for path in sorted(pages_dir.glob("*.json")):
            relative = f"pages/{path.name}"
            data, found = _validate_document(root, relative, "page.schema.json")
            issues.extend(found)
            if data is None:
                continue
            _validate_sections(root, relative, data, site, issues, warnings)
            slug = data.get("slug", "")
            if slug in pages:
                issues.append(ConfigIssue("error", relative, "$.slug", f"Duplicate page slug {slug!r}."))
            else:
                pages[slug] = data

    navigation = documents["navigation.json"]
    seen_ids: set[str] = set()
    for index, item in enumerate(navigation.get("items", [])):
        if item["id"] in seen_ids:
            issues.append(ConfigIssue("error", "navigation.json", f"$.items[{index}].id", "Duplicate navigation id."))
        seen_ids.add(item["id"])
        _check_href("navigation.json", f"$.items[{index}].href", item.get("href", ""), issues)
    for column_index, column in enumerate(navigation.get("footer", {}).get("columns", [])):
        for link_index, link in enumerate(column.get("links", [])):
            _check_href(
                "navigation.json",
                f"$.footer.columns[{column_index}].links[{link_index}].href",
                link.get("href", ""),
                issues,
            )

    services = _load_collection(root, "services", "service.schema.json", issues, warnings)
    portfolio = _load_collection(root, "portfolio", "portfolio.schema.json", issues, warnings)
    if issues:
        raise ConfigError(issues)

    try:
        theme_css = build_theme_css(documents["theme.json"])
    except ValueError as exc:
        raise ConfigError([ConfigIssue("error", "theme.json", "$.colors", str(exc))]) from exc

    return SiteBundle(
        site=site,
        theme=documents["theme.json"],
        theme_css=theme_css,
        navigation=navigation,
        pages=pages,
        services=services,
        portfolio=portfolio,
        warnings=warnings,
    )


def _signature(root: Path) -> tuple:
    if not root.exists():
        return ("missing",)
    files = []
    for path in sorted(root.rglob("*.json")):
        try:
            contained = contained_directory(root, path)
        except ValueError:
            continue
        stat = contained.stat()
        files.append((str(contained.relative_to(root.resolve())), stat.st_mtime_ns, stat.st_size))
    return tuple(files)


def get_bundle() -> SiteBundle:
    root = config_root()
    key = (str(root.resolve()) if root.exists() else str(root), _signature(root))
    with _LOCK:
        if _CACHE["key"] == key and _CACHE["bundle"] is not None:
            return _CACHE["bundle"]
        try:
            bundle = load_bundle(root)
        except ConfigError:
            logger.exception("Site configuration failed validation.")
            if _CACHE["last_valid"] is not None and _CACHE["last_valid_root"] == str(root):
                logger.error("Serving the last valid site configuration.")
                return _CACHE["last_valid"]
            raise
        for warning in bundle.warnings:
            logger.warning("%s", warning)
        _CACHE["key"] = key
        _CACHE["bundle"] = bundle
        _CACHE["last_valid"] = bundle
        _CACHE["last_valid_root"] = str(root)
        return bundle
