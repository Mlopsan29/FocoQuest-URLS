from django.urls import path, re_path
from . import views

# URL 6 
path('estudiantes/ranking/', views.ranking_estudiantes, name='ranking_estudiantes'),