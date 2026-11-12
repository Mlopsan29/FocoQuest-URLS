from django.shortcuts import render
from django.core.exceptions import BadRequest, PermissionDenied
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador
from django.db.models import Q, Avg, Min, Max, Count
# Create your views here.

# URL 8: estudiantes que no tienen ningún logro.
# Usa un filtro con None sobre la TABLA INTERMEDIA ObtencionLogro (a través de su related_name "obtenciones"):
# filter(obtenciones=None) devuelve los estudiantes que no tienen ninguna fila en esa tabla. De cada estudiante se
# muestra toda su información, su usuario y su mascota (OneToOne) y sus psicólogos favoritos (ManyToMany) con su
# usuario y sus especialidades.
def estudiantes_sin_logros(request):
    # SELECT e.*, u.*, m.*
    # FROM FocoQuest_estudiante e
    #   LEFT OUTER JOIN FocoQuest_obtencionlogro o ON e.id = o.estudiante_id
    #   INNER JOIN auth_user u ON e.user_id = u.id
    #   LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
    # WHERE o.id IS NULL
    # ORDER BY u.username ASC;
    #
    # SELECT p.*, ef.estudiante_id FROM FocoQuest_psicologo p
    #   INNER JOIN FocoQuest_estudiante_psicologos_favoritos ef ON p.id = ef.psicologo_id
    #   WHERE ef.estudiante_id IN (ids de los estudiantes anteriores);
    # SELECT u.* FROM auth_user u WHERE u.id IN (user_id de esos psicólogos);
    # SELECT esp.*, pe.psicologo_id FROM FocoQuest_especialidad esp
    #   INNER JOIN FocoQuest_psicologo_especialidades pe ON esp.id = pe.especialidad_id
    #   WHERE pe.psicologo_id IN (ids de esos psicólogos);
    estudiantes = Estudiante.objects.select_related("user", "mascota")
    estudiantes = estudiantes.prefetch_related("psicologos_favoritos__user", "psicologos_favoritos__especialidades")
    estudiantes = estudiantes.filter(obtenciones=None).order_by("user__username")
    return render(request, 'FocoQuest/estudiante/sin_logros.html', {"estudiantes": estudiantes})