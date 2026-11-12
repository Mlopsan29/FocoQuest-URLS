from django.urls import path, re_path
from . import views

urlpatterns = [
# URL 4
path('estudiantes/destacados/', views.estudiantes_destacados, name='estudiantes_destacados'),
]