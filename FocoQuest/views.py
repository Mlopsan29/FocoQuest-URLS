from django.shortcuts import render
from django.core.exceptions import BadRequest, PermissionDenied
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador
from django.db.models import Q, Avg, Min, Max, Count

# Create your views here.
# # URL 10: trabajadores y sus psicólogos favoritos.
# Muestra todos los trabajadores ordenados por apellido (order_by sobre un campo de la tabla User relacionada).
# De cada uno se muestra toda su información, su usuario (OneToOne) y sus psicólogos favoritos (ManyToMany), y de
# cada psicólogo su usuario (OneToOne, opcional) y todas sus especialidades (ManyToMany).
def trabajadores_favoritos(request):
    # SELECT t.*, u.*
    # FROM FocoQuest_trabajador t
    #   INNER JOIN auth_user u ON t.user_id = u.id
    # ORDER BY u.last_name ASC;
    #
    # SELECT p.*, tf.trabajador_id FROM FocoQuest_psicologo p
    #   INNER JOIN FocoQuest_trabajador_psicologos_favoritos tf ON p.id = tf.psicologo_id
    #   WHERE tf.trabajador_id IN (ids de los trabajadores anteriores);
    # SELECT u.* FROM auth_user u WHERE u.id IN (user_id de esos psicólogos);
    # SELECT esp.*, pe.psicologo_id FROM FocoQuest_especialidad esp
    #   INNER JOIN FocoQuest_psicologo_especialidades pe ON esp.id = pe.especialidad_id
    #   WHERE pe.psicologo_id IN (ids de esos psicólogos);
    trabajadores = Trabajador.objects.select_related("user")
    trabajadores = trabajadores.prefetch_related("psicologos_favoritos__user", "psicologos_favoritos__especialidades")
    trabajadores = trabajadores.order_by("user__last_name")
    return render(request, 'FocoQuest/trabajador/favoritos.html', {"trabajadores": trabajadores})