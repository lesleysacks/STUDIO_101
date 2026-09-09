from django.contrib import admin
from .models import ProjectCategory, Project, ProjectImage

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3
    fields = ('image', 'caption', 'is_full_width', 'order')

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client_name', 'category', 'is_featured', 'is_published', 'order')
    list_filter = ('category', 'is_featured', 'is_published')
    search_fields = ('title', 'client_name', 'summary', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectImageInline]
    list_editable = ('is_featured', 'is_published', 'order')
