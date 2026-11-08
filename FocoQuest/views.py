from django.shortcuts import render
from .models import Temario, Psicologo, Estudiante, ObtencionLogro, Trabajador


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
