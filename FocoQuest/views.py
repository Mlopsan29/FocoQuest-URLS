from django.shortcuts import render
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador

# Create your views here.
def ranking_estudiantes(request):
    estudiantes = Estudiante.objects.select_related("user", "mascota").prefetch_related("temarios")
    estudiantes = estudiantes.order_by("-xp")[:3]
    return render(request, 'FocoQuest/estudiante/ranking.html', {"estudiantes": estudiantes})