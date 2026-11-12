from django.urls import path, re_path
from . import views

# URL 7 
re_path(r'^estudiantes/examen/(?P<anio>[0-9]{4})/$', views.estudiantes_examen_anio, name='estudiantes_examen_anio'),
