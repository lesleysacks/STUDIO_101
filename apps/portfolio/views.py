from django.http import Http404
from django.shortcuts import render

from apps.siteconfig.services.catalog import json_project_namespace
from apps.siteconfig.services.errors import ConfigError
from apps.siteconfig.services.loader import get_bundle
from apps.siteconfig.services.rendering import render_configured_page

from .models import Project, ProjectCategory


def portfolio_list_view(request):
    category_slug = request.GET.get("category")

    def fallback():
        projects = Project.objects.filter(is_published=True).order_by("order")
        if category_slug:
            projects = projects.filter(category__slug=category_slug)
        return {
            "projects": projects,
            "categories": ProjectCategory.objects.all(),
            "selected_category": category_slug,
        }

    if category_slug:
        return render(request, "pages/portfolio_list.html", fallback())
    return render_configured_page(request, "portfolio", "pages/portfolio_list.html", fallback)


def project_detail_view(request, slug):
    project = Project.objects.filter(slug=slug, is_published=True).first()
    if project is not None:
        gallery_images = project.gallery_images.all().order_by("order")
        related_projects = Project.objects.filter(
            category=project.category, is_published=True
        ).exclude(id=project.id)[:3]
        return render(request, "pages/project_detail.html", {
            "project": project,
            "gallery_images": gallery_images,
            "related_projects": related_projects,
        })
    try:
        bundle = get_bundle()
    except ConfigError as exc:
        raise Http404("Project not found") from exc
    entry = bundle.portfolio.get(slug)
    if entry is None or not entry.get("published", True):
        raise Http404("Project not found")
    project, gallery_images = json_project_namespace(entry)
    seo = entry.get("seo") or {}
    return render(request, "pages/project_detail.html", {
        "project": project,
        "gallery_images": gallery_images,
        "related_projects": [],
        "page_title": seo.get("title") or project.title,
        "page_description": seo.get("description") or project.summary,
    })
