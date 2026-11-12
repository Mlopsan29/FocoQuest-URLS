from django.shortcuts import render
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador
# Create your views here.

# URL 7: estudiantes con algún examen en un año concreto (URL con re_path y expresión regular).
# El año llega como cuatro dígitos (re_path con (?P<anio>[0-9]{4})). Se buscan los estudiantes que tienen algún
# temario cuya fecha de examen cae en ese año, usando la RELACIÓN REVERSA desde Estudiante hacia Temario
# (related_name="temarios"): filter(temarios__fecha_examen__year=anio). distinct() evita que un estudiante salga
# repetido si tiene varios exámenes ese año. Se muestra toda la información del estudiante, su usuario y su
# mascota (OneToOne) y todos sus temarios (ManyToOne inverso).
def estudiantes_examen_anio(request, anio):
    # SELECT DISTINCT e.*, u.*, m.*
    # FROM FocoQuest_estudiante e
    #   INNER JOIN FocoQuest_temario t ON e.id = t.estudiante_id
    #   INNER JOIN auth_user u ON e.user_id = u.id
    #   LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
    # WHERE t.fecha_examen BETWEEN 'anio-01-01' AND 'anio-12-31'
    # ORDER BY u.username ASC;
    #
    # SELECT t.* FROM FocoQuest_temario t WHERE t.estudiante_id IN (ids de los estudiantes anteriores);
    estudiantes = Estudiante.objects.select_related("user", "mascota").prefetch_related("temarios")
    estudiantes = estudiantes.filter(temarios__fecha_examen__year=anio).distinct().order_by("user__username")
    return render(request, 'FocoQuest/estudiante/examenes_anio.html', {"estudiantes": estudiantes, "anio": anio})