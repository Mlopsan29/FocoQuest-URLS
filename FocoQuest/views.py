from django.shortcuts import render
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador
from django.db.models import Q, Avg, Min, Max, Count

# Index: muestra el listado de enlaces desde el que se accede a todas las URLs de la aplicación.
def index(request):
    return render(request, 'index.html')

# URL 1: temarios de un estudiante.
# Recibe un parámetro ENTERO (el id del estudiante) y muestra todos sus temarios ordenados por fecha de examen
# (ManyToOne: un estudiante tiene muchos temarios). De cada temario se muestra también toda la información de su
# estudiante, del usuario del estudiante (OneToOne) y de su mascota (OneToOne). Usa select_related para traer
# todo con una sola consulta.
def temarios_estudiante(request, id_estudiante):
    temarios = Temario.objects.select_related("estudiante__user", "estudiante__mascota")
    temarios = temarios.filter(estudiante=id_estudiante).order_by("fecha_examen")
    return render(request, 'temarios.html', {"temarios": temarios, "id_estudiante": id_estudiante})

# SELECT t.*, e.*, u.*, m.*
    # FROM FocoQuest_temario t
    #   INNER JOIN FocoQuest_estudiante e ON t.estudiante_id = e.id
    #   INNER JOIN auth_user u ON e.user_id = u.id
    #   LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
    # WHERE t.estudiante_id = id_estudiante
    # ORDER BY t.fecha_examen ASC;
    
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


# URL 3: psicólogos por modalidad y precio máximo.
# Recibe DOS parámetros (un string con la modalidad y un entero con el precio máximo por sesión) y muestra los
# psicólogos que cumplen LAS DOS condiciones a la vez (filtro con AND), ordenados del más barato al más caro.
# Para cada psicólogo se muestra toda su información, su usuario (OneToOne, opcional) y todas sus especialidades
# (ManyToMany).
def psicologos_modalidad_precio(request, modalidad, precio_maximo):
    psicologos = Psicologo.objects.select_related("user").prefetch_related("especialidades")
    psicologos = psicologos.filter(modalidad=modalidad, precio_sesion__lte=precio_maximo).order_by("precio_sesion")
    return render(request, 'por_modalidad_precio.html', {"psicologos": psicologos, "modalidad": modalidad, "precio_maximo": precio_maximo})

# SELECT p.*, u.*
    # FROM FocoQuest_psicologo p
    #   LEFT OUTER JOIN auth_user u ON p.user_id = u.id
    # WHERE p.modalidad = 'modalidad' AND p.precio_sesion <= precio_maximo
    # ORDER BY p.precio_sesion ASC;
    #
    # SELECT esp.*, pe.psicologo_id FROM FocoQuest_especialidad esp
    #   INNER JOIN FocoQuest_psicologo_especialidades pe ON esp.id = pe.especialidad_id
    #   WHERE pe.psicologo_id IN (ids de los psicólogos anteriores);


# URL 4: estudiantes destacados.
# Muestra los estudiantes con nivel 8 o superior, o con una racha actual de 10 días o más (filtro con OR), del
# nivel más alto al más bajo. De cada uno se muestra toda su información, su usuario y su mascota (OneToOne) y sus
# logros (ManyToMany con tabla intermedia: se muestran los datos de ObtencionLogro y de cada Logro).
# INVESTIGACIÓN: el OR no se puede hacer con filter(a, b) porque eso es un AND. Se usan objetos Q (importados de
# django.db.models) unidos con el operador "|":  Q(condición1) | Q(condición2).
def estudiantes_destacados(request):
    estudiantes = Estudiante.objects.select_related("user", "mascota").prefetch_related("obtenciones__logro")
    estudiantes = estudiantes.filter(Q(nivel__gte=8) | Q(racha_actual__gte=10)).order_by("-nivel")
    return render(request, 'destacados.html', {"estudiantes": estudiantes})

# SELECT e.*, u.*, m.*
    # FROM FocoQuest_estudiante e
    #   INNER JOIN auth_user u ON e.user_id = u.id
    #   LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
    # WHERE (e.nivel >= 8 OR e.racha_actual >= 10)
    # ORDER BY e.nivel DESC;
    #
    # SELECT o.* FROM FocoQuest_obtencionlogro o WHERE o.estudiante_id IN (ids de los estudiantes anteriores);
    # SELECT l.* FROM FocoQuest_logro l WHERE l.id IN (logro_id de esas obtenciones);


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
    return render(request, 'estadisticas.html', {"estadisticas": estadisticas, "sin_precio": sin_precio, "psicologos": psicologos})

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
    return render(request, 'ranking.html', {"estudiantes": estudiantes})
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
    return render(request, 'estudiante/examenes_anio.html', {"estudiantes": estudiantes, "anio": anio})

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
    estudiantes = Estudiante.objects.select_related("user", "mascota")
    estudiantes = estudiantes.prefetch_related("psicologos_favoritos__user", "psicologos_favoritos__especialidades")
    estudiantes = estudiantes.filter(obtenciones=None).order_by("user__username")
    return render(request, 'estudiante/sin_logros.html', {"estudiantes": estudiantes})

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
    return render(request, 'logro/estudiantes.html', {"obtenciones": obtenciones, "id_logro": id_logro})
    

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
    return render(request, 'trabajador/favoritos.html', {"trabajadores": trabajadores})

# Error 400: petición incorrecta.
def mi_error_400(request, exception=None):
    return render(request, '400.html', None, None, 400)


# Error 403: acceso prohibido.
def mi_error_403(request, exception=None):
    return render(request, '403.html', None, None, 403)


# Error 404: página no encontrada.
def mi_error_404(request, exception=None):
    return render(request, '404.html', None, None, 404)


# Error 500: error interno del servidor.
def mi_error_500(request, exception=None):
    return render(request, '500.html', None, None, 500)

def probar_error_400(request):
    raise SuspiciousOperation("Prueba de error 400")
 
 
def probar_error_403(request):
    raise PermissionDenied("Prueba de error 403")
 
 
def probar_error_500(request):
    raise Exception("Prueba de error 500")
