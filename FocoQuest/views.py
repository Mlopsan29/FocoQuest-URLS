from django.shortcuts import render
from .models import Psicologo


# URL 3: psicólogos por modalidad y precio máximo.
# Recibe DOS parámetros (un string con la modalidad y un entero con el precio máximo por sesión) y muestra los
# psicólogos que cumplen LAS DOS condiciones a la vez (filtro con AND), ordenados del más barato al más caro.
# Para cada psicólogo se muestra toda su información, su usuario (OneToOne, opcional) y todas sus especialidades
# (ManyToMany).
def psicologos_modalidad_precio(request, modalidad, precio_maximo):
    psicologos = Psicologo.objects.select_related("user").prefetch_related("especialidades")
    psicologos = psicologos.filter(modalidad=modalidad, precio_sesion__lte=precio_maximo).order_by("precio_sesion")
    return render(request, 'FocoQuest/psicologo/por_modalidad_precio.html', {"psicologos": psicologos, "modalidad": modalidad, "precio_maximo": precio_maximo})

# SELECT p.*, u.*
    # FROM FocoQuest_psicologo p
    #   LEFT OUTER JOIN auth_user u ON p.user_id = u.id
    # WHERE p.modalidad = 'modalidad' AND p.precio_sesion <= precio_maximo
    # ORDER BY p.precio_sesion ASC;
    #
    # SELECT esp.*, pe.psicologo_id FROM FocoQuest_especialidad esp
    #   INNER JOIN FocoQuest_psicologo_especialidades pe ON esp.id = pe.especialidad_id
    #   WHERE pe.psicologo_id IN (ids de los psicólogos anteriores);