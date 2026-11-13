from django.urls import path, re_path
from . import views

urlpatterns = [
# URL 1
path('estudiante/<int:id_estudiante>/temarios/', views.temarios_estudiante, name='temarios_estudiante'),
    
# URL 2
path('psicologos/especialidad/<str:nombre_especialidad>/', views.psicologos_especialidad, name='psicologos_especialidad'),

    # URL 3
path('psicologos/<str:modalidad>/<int:precio_maximo>/', views.psicologos_modalidad_precio, name='psicologos_modalidad_precio'),

# URL 4
path('estudiantes/destacados/', views.estudiantes_destacados, name='estudiantes_destacados'),

# URL 5
path('psicologos/estadisticas/', views.psicologos_estadisticas, name='psicologos_estadisticas'),
]
