from django.urls import path, re_path
from . import views

urlpatterns = [
    # URL 1
    path('estudiante/<int:id_estudiante>/temarios/', views.temarios_estudiante, name='temarios_estudiante'),
]
# URL 2
urlpatterns = [
path('', views.index, name='index'),
path('psicologos/especialidad/<str:nombre_especialidad>/', views.psicologos_especialidad, name='psicologos_especialidad'),
]

