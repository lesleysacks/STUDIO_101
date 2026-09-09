from django.shortcuts import render
from .models import StudioSpace, Equipment

def studio_overview_view(request):
    spaces = StudioSpace.objects.filter(is_available=True)
    equipment = Equipment.objects.all()
    return render(request, 'pages/studio.html', {
        'spaces': spaces,
        'equipment': equipment,
    })
