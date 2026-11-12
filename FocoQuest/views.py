from django.shortcuts import render
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador
# Create your views here.

def estudiantes_examen_anio(request, anio):
    estudiantes = Estudiante.objects.select_related("user", "mascota").prefetch_related("temarios")
    estudiantes = estudiantes.filter(temarios__fecha_examen__year=anio).distinct().order_by("user__username")
    return render(request, 'FocoQuest/estudiante/examenes_anio.html', {"estudiantes": estudiantes, "anio": anio})