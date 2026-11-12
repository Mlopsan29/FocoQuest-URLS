from django.shortcuts import render
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador

# Create your views here.
# URL 6: ranking de los 3 estudiantes con más experiencia.
# Ordena los estudiantes por XP de mayor a menor (order_by) y se queda solo con los 3 primeros (limit: el
# troceado [:3] de Python se traduce en LIMIT 3). De cada uno se muestra toda su información, su usuario y su
# mascota (OneToOne) y todos sus temarios (ManyToOne inverso con related_name="temarios").
def ranking_estudiantes(request):
    # SELECT e.*, u.*, m.*
    # FROM FocoQuest_estudiante e
    #   INNER JOIN auth_user u ON e.user_id = u.id
    #   LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
    # ORDER BY e.xp DESC
    # LIMIT 3;
    #
    # SELECT t.* FROM FocoQuest_temario t WHERE t.estudiante_id IN (ids de los 3 estudiantes);
    estudiantes = Estudiante.objects.select_related("user", "mascota").prefetch_related("temarios")
    estudiantes = estudiantes.order_by("-xp")[:3]
    return render(request, 'FocoQuest/estudiante/ranking.html', {"estudiantes": estudiantes})