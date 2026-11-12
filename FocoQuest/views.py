from django.shortcuts import render
from django.core.exceptions import BadRequest, PermissionDenied
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador
from django.db.models import Q, Avg, Min, Max, Count
# Create your views here.

# URL 9: estudiantes que han obtenido un logro.
# Recibe un parámetro ENTERO (el id del logro) y consulta directamente la TABLA INTERMEDIA ObtencionLogro, que
# tiene dos relaciones ManyToOne: hacia el logro y hacia el estudiante (así se resuelve el ManyToMany Estudiante
# ↔ Logro). Ordena por progreso de mayor a menor. De cada fila se muestra toda la información de la obtención,
# del logro, del estudiante, de su usuario y de su mascota (OneToOne).
def estudiantes_logro(request, id_logro):
    # SELECT o.*, l.*, e.*, u.*, m.*
    # FROM FocoQuest_obtencionlogro o
    #   INNER JOIN FocoQuest_estudiante e ON o.estudiante_id = e.id
    #   INNER JOIN auth_user u ON e.user_id = u.id
    #   LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
    #   INNER JOIN FocoQuest_logro l ON o.logro_id = l.id
    # WHERE o.logro_id = id_logro
    # ORDER BY o.progreso DESC;
    obtenciones = ObtencionLogro.objects.select_related("estudiante__user", "estudiante__mascota", "logro")
    obtenciones = obtenciones.filter(logro=id_logro).order_by("-progreso")
    return render(request, 'FocoQuest/logro/estudiantes.html', {"obtenciones": obtenciones, "id_logro": id_logro})
