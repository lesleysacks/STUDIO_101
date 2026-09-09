from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectCategory

def portfolio_list_view(request):
    projects = Project.objects.filter(is_published=True).order_by('order')
    categories = ProjectCategory.objects.all()
    
    category_slug = request.GET.get('category')
    if category_slug:
        projects = projects.filter(category__slug=category_slug)

    return render(request, 'pages/portfolio_list.html', {
        'projects': projects,
        'categories': categories,
        'selected_category': category_slug,
    })

def project_detail_view(request, slug):
    project = get_object_or_404(Project, slug=slug, is_published=True)
    gallery_images = project.gallery_images.all().order_by('order')
    related_projects = Project.objects.filter(category=project.category, is_published=True).exclude(id=project.id)[:3]

    return render(request, 'pages/project_detail.html', {
        'project': project,
        'gallery_images': gallery_images,
        'related_projects': related_projects,
    })
