from django.urls import path, re_path
from . import views

path('logro/<int:id_logro>/estudiantes/', views.estudiantes_logro, name='estudiantes_logro'),