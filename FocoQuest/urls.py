from django.urls import path, re_path
from . import views

path('trabajadores/favoritos/', views.trabajadores_favoritos, name='trabajadores_favoritos'),
