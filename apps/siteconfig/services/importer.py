"""Import and export service and portfolio catalogs without silent overwrites."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.files.base import ContentFile
from django.db import transaction

from apps.portfolio.models import Project, ProjectCategory
from apps.services.models import Service, ServiceCategory, ServiceFeature

from .loader import config_root, load_bundle
from .security import static_file


@dataclass
class ImportPlan:
    creates: list[str] = field(default_factory=list)
    updates: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and not self.conflicts


def _write_image(instance, field_name: str, relative: str) -> None:
    path = static_file(relative)
    if path is None:
        return
    getattr(instance, field_name).save(path.name, ContentFile(path.read_bytes()), save=False)


def _same_price(current, incoming) -> bool:
    if current is None and incoming in (None, ""):
        return True
    if current is None or incoming in (None, ""):
        return False
    try:
        return Decimal(str(current)) == Decimal(str(incoming))
    except (InvalidOperation, ValueError):
        return False


def _service_changed(service: Service, entry: dict) -> bool:
    category_name = (entry.get("category") or {}).get("name", "")
    current_category = service.category.name if service.category_id else ""
    return any(
        [
            service.title != entry.get("name", ""),
            service.summary != entry.get("summary", ""),
            service.full_description != entry.get("description", ""),
            not _same_price(service.starting_price, entry.get("starting_price")),
            service.duration_label != entry.get("duration_label", ""),
            service.price_unit != entry.get("price_unit", ""),
            service.is_featured != entry.get("is_featured", False),
            service.order != entry.get("order", 0),
            current_category != category_name,
        ]
    )


def plan_services(bundle=None) -> ImportPlan:
    bundle = bundle or load_bundle(config_root())
    plan = ImportPlan()
    for slug, entry in sorted(bundle.services.items()):
        if not entry.get("published", True):
            continue
        existing = Service.objects.filter(slug=slug).first()
        if existing is None:
            plan.creates.append(slug)
        elif _service_changed(existing, entry):
            plan.conflicts.append(slug)
            plan.updates.append(slug)
        else:
            plan.unchanged.append(slug)
    return plan


def apply_services(*, update: bool) -> ImportPlan:
    bundle = load_bundle(config_root())
    plan = plan_services(bundle)
    if plan.conflicts and not update:
        return plan
    with transaction.atomic():
        for slug, entry in sorted(bundle.services.items()):
            if not entry.get("published", True):
                continue
            category_data = entry.get("category") or {}
            category = None
            if category_data.get("slug") and category_data.get("name"):
                category, _created = ServiceCategory.objects.get_or_create(
                    slug=category_data["slug"],
                    defaults={"name": category_data["name"], "description": category_data.get("description", "")},
                )
            existing = Service.objects.filter(slug=slug).first()
            if existing and not update:
                continue
            service = existing or Service(slug=slug)
            service.category = category
            service.title = entry.get("name", "")
            service.summary = entry.get("summary", "")
            service.full_description = entry.get("description", "")
            service.starting_price = entry.get("starting_price")
            service.duration_label = entry.get("duration_label", "")
            service.price_unit = entry.get("price_unit", "")
            service.is_featured = entry.get("is_featured", False)
            service.order = entry.get("order", 0)
            if not service.featured_image:
                _write_image(service, "featured_image", entry.get("featured_image", ""))
            service.save()
            if update or existing is None:
                service.features.all().delete()
                for index, feature in enumerate(entry.get("features", [])):
                    ServiceFeature.objects.create(
                        service=service,
                        title=feature.get("title", ""),
                        description=feature.get("description", ""),
                        order=index,
                    )
    if update:
        plan.conflicts.clear()
    return plan


def export_services() -> list[dict]:
    records = []
    for service in Service.objects.select_related("category").all():
        records.append(
            {
                "schema_version": 1,
                "slug": service.slug,
                "name": service.title,
                "summary": service.summary,
                "description": service.full_description,
                "category": {
                    "slug": service.category.slug,
                    "name": service.category.name,
                }
                if service.category_id
                else {},
                "starting_price": float(service.starting_price) if service.starting_price is not None else None,
                "price_unit": service.price_unit,
                "duration_label": service.duration_label,
                "is_featured": service.is_featured,
                "order": service.order,
                "published": True,
                "features": [
                    {"title": feature.title, "description": feature.description}
                    for feature in service.features.all()
                ],
                "cta_label": "Book This Service",
                "cta_href": "/book/",
            }
        )
    return records


def plan_portfolio(bundle=None) -> ImportPlan:
    bundle = bundle or load_bundle(config_root())
    plan = ImportPlan()
    for slug, entry in sorted(bundle.portfolio.items()):
        if not entry.get("published", True):
            continue
        existing = Project.objects.filter(slug=slug).first()
        if existing is None:
            if not (entry.get("category") or {}).get("slug"):
                plan.errors.append(f"{slug}: category.slug is required to create a portfolio record.")
            else:
                plan.creates.append(slug)
        else:
            plan.conflicts.append(slug)
            plan.updates.append(slug)
    return plan


def apply_portfolio(*, update: bool) -> ImportPlan:
    bundle = load_bundle(config_root())
    plan = plan_portfolio(bundle)
    if plan.errors or (plan.conflicts and not update):
        return plan
    with transaction.atomic():
        for slug, entry in sorted(bundle.portfolio.items()):
            if not entry.get("published", True):
                continue
            category_data = entry.get("category") or {}
            if not category_data.get("slug"):
                continue
            category, _created = ProjectCategory.objects.get_or_create(
                slug=category_data["slug"],
                defaults={"name": category_data.get("name") or category_data["slug"]},
            )
            existing = Project.objects.filter(slug=slug).first()
            if existing and not update:
                continue
            project = existing or Project(slug=slug, category=category)
            project.category = category
            project.title = entry.get("title", "")
            project.client_name = entry.get("client_name", "")
            project.summary = entry.get("summary", "")
            project.description = entry.get("description", "")
            project.is_featured = entry.get("is_featured", False)
            project.is_published = True
            project.order = entry.get("order", 0)
            if not project.cover_image:
                _write_image(project, "cover_image", entry.get("image", ""))
            project.save()
    if update:
        plan.conflicts.clear()
    return plan


def export_portfolio() -> list[dict]:
    records = []
    for project in Project.objects.select_related("category").filter(is_published=True):
        records.append(
            {
                "schema_version": 1,
                "slug": project.slug,
                "title": project.title,
                "client_name": project.client_name,
                "summary": project.summary,
                "description": project.description,
                "category": {"slug": project.category.slug, "name": project.category.name},
                "is_featured": project.is_featured,
                "published": project.is_published,
                "order": project.order,
                "image_alt": project.title,
            }
        )
    return records


def dump_json(payload) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def write_output(payload, output: Path | None) -> str:
    text = dump_json(payload)
    if output is None:
        return text
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(output)
    return text
