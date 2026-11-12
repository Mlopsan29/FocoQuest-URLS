from django.shortcuts import render
from .models import Estudiante
from django.db.models import Q


# URL 4: estudiantes destacados.
# Muestra los estudiantes con nivel 8 o superior, o con una racha actual de 10 días o más (filtro con OR), del
# nivel más alto al más bajo. De cada uno se muestra toda su información, su usuario y su mascota (OneToOne) y sus
# logros (ManyToMany con tabla intermedia: se muestran los datos de ObtencionLogro y de cada Logro).
# INVESTIGACIÓN: el OR no se puede hacer con filter(a, b) porque eso es un AND. Se usan objetos Q (importados de
# django.db.models) unidos con el operador "|":  Q(condición1) | Q(condición2).
def estudiantes_destacados(request):
    estudiantes = Estudiante.objects.select_related("user", "mascota").prefetch_related("obtenciones__logro")
    estudiantes = estudiantes.filter(Q(nivel__gte=8) | Q(racha_actual__gte=10)).order_by("-nivel")
    return render(request, 'FocoQuest/estudiante/destacados.html', {"estudiantes": estudiantes})

# SELECT e.*, u.*, m.*
    # FROM FocoQuest_estudiante e
    #   INNER JOIN auth_user u ON e.user_id = u.id
    #   LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
    # WHERE (e.nivel >= 8 OR e.racha_actual >= 10)
    # ORDER BY e.nivel DESC;
    #
    # SELECT o.* FROM FocoQuest_obtencionlogro o WHERE o.estudiante_id IN (ids de los estudiantes anteriores);
    # SELECT l.* FROM FocoQuest_logro l WHERE l.id IN (logro_id de esas obtenciones);