from django.shortcuts import render
from django.core.exceptions import BadRequest, PermissionDenied
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador
from django.db.models import Q, Avg, Min, Max, Count


# URL 5: estadísticas de precios de los psicólogos (AGGREGATE).
# Calcula con aggregate() el número de psicólogos con precio, el precio medio, el mínimo y el máximo, y cuenta
# cuántos no tienen precio (filtro con None: precio_sesion=None, es decir IS NULL). Además lista esos psicólogos
# con todo su detalle (usuario OneToOne y especialidades ManyToMany), del más barato al más caro.
# INVESTIGACIÓN: aggregate() (con funciones de django.db.models como Count, Avg, Min y Max) calcula un valor
# sobre TODAS las filas del queryset y devuelve un diccionario, no un queryset. Por eso no se le puede encadenar
# .filter() después, pero sí se le pueden aplicar antes.
def psicologos_estadisticas(request):
    con_precio = Psicologo.objects.filter(precio_sesion__isnull=False)

    # SELECT COUNT(p.id) AS total, AVG(p.precio_sesion) AS precio_medio,
    #        MIN(p.precio_sesion) AS precio_minimo, MAX(p.precio_sesion) AS precio_maximo
    # FROM FocoQuest_psicologo p
    # WHERE p.precio_sesion IS NOT NULL;
    estadisticas = con_precio.aggregate(total=Count("id"), precio_medio=Avg("precio_sesion"), precio_minimo=Min("precio_sesion"), precio_maximo=Max("precio_sesion"))

    # SELECT COUNT(*) FROM FocoQuest_psicologo p WHERE p.precio_sesion IS NULL;
    sin_precio = Psicologo.objects.filter(precio_sesion=None).count()

    # SELECT p.*, u.* FROM FocoQuest_psicologo p
    #   LEFT OUTER JOIN auth_user u ON p.user_id = u.id
    # WHERE p.precio_sesion IS NOT NULL
    # ORDER BY p.precio_sesion ASC;
    # + SELECT esp.*, pe.psicologo_id FROM FocoQuest_especialidad esp
    #     INNER JOIN FocoQuest_psicologo_especialidades pe ON esp.id = pe.especialidad_id
    #     WHERE pe.psicologo_id IN (ids de los psicólogos anteriores);
    psicologos = con_precio.select_related("user").prefetch_related("especialidades").order_by("precio_sesion")
    return render(request, 'FocoQuest/psicologo/estadisticas.html', {"estadisticas": estadisticas, "sin_precio": sin_precio, "psicologos": psicologos})