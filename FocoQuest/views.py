from django.shortcuts import render
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador


# URL 2: psicólogos de una especialidad.
# Recibe un parámetro STRING y muestra los psicólogos que la tienen
# (ManyToMany: un psicólogo tiene varias especialidades). De cada psicólogo se muestra toda su información, su
# usuario (OneToOne, opcional), TODAS sus especialidades y los estudiantes y trabajadores que lo tienen como
# favorito (relaciones inversas por related_name: seguidores_estudiantes y seguidores_trabajadores).
# __icontains = "contiene el texto sin distinguir mayúsculas" (LIKE '%texto%'). distinct() evita repetidos si un
# psicólogo coincide con varias especialidades.
def psicologos_especialidad(request, nombre_especialidad):
    psicologos = Psicologo.objects.select_related("user")
    psicologos = psicologos.prefetch_related("especialidades", "seguidores_estudiantes__user", "seguidores_trabajadores__user")
    psicologos = psicologos.filter(especialidades__nombre__icontains=nombre_especialidad).distinct().order_by("nombre_completo")
    return render(request, 'por_especialidad.html', {"psicologos": psicologos, "nombre_especialidad": nombre_especialidad})

# SELECT DISTINCT p.*, u.*
    # FROM FocoQuest_psicologo p
    #   INNER JOIN FocoQuest_psicologo_especialidades pe ON p.id = pe.psicologo_id
    #   INNER JOIN FocoQuest_especialidad esp ON pe.especialidad_id = esp.id
    #   LEFT OUTER JOIN auth_user u ON p.user_id = u.id
    # WHERE esp.nombre LIKE '%nombre_especialidad%'
    # ORDER BY p.nombre_completo ASC;
    
#Después prefetch_related lanza una consulta por cada relación ManyToMany/inversa (todas con IN):
    # SELECT esp.*, pe.psicologo_id FROM FocoQuest_especialidad esp
    #   INNER JOIN FocoQuest_psicologo_especialidades pe ON esp.id = pe.especialidad_id
    #   WHERE pe.psicologo_id IN (ids de los psicólogos anteriores);
    # SELECT e.*, ef.psicologo_id FROM FocoQuest_estudiante e
    #   INNER JOIN FocoQuest_estudiante_psicologos_favoritos ef ON e.id = ef.estudiante_id
    #   WHERE ef.psicologo_id IN (...);
    # SELECT u.* FROM auth_user u WHERE u.id IN (user_id de esos estudiantes);
    # SELECT t.*, tf.psicologo_id FROM FocoQuest_trabajador t
    #   INNER JOIN FocoQuest_trabajador_psicologos_favoritos tf ON t.id = tf.trabajador_id
    #   WHERE tf.psicologo_id IN (...);
    # SELECT u.* FROM auth_user u WHERE u.id IN (user_id de esos trabajadores);
