from django.shortcuts import render
from django.core.exceptions import BadRequest, PermissionDenied
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador
from django.db.models import Q, Avg, Min, Max, Count
# Create your views here.

def estudiantes_sin_logros(request):
    estudiantes = Estudiante.objects.select_related("user", "mascota")
    estudiantes = estudiantes.prefetch_related("psicologos_favoritos__user", "psicologos_favoritos__especialidades")
    estudiantes = estudiantes.filter(obtenciones=None).order_by("user__username")
    return render(request, 'FocoQuest/estudiante/sin_logros.html', {"estudiantes": estudiantes})