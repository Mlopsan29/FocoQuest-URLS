from django.shortcuts import render
from django.core.exceptions import BadRequest, PermissionDenied
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador
from django.db.models import Q, Avg, Min, Max, Count
# Create your views here.

def estudiantes_logro(request, id_logro):
    obtenciones = ObtencionLogro.objects.select_related("estudiante__user", "estudiante__mascota", "logro")
    obtenciones = obtenciones.filter(logro=id_logro).order_by("-progreso")
    return render(request, 'FocoQuest/logro/estudiantes.html', {"obtenciones": obtenciones, "id_logro": id_logro})