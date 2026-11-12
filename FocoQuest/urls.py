from django.urls import path, re_path
from . import views

urlpatterns = [
    # URL 1
    path('estudiante/<int:id_estudiante>/temarios/', views.temarios_estudiante, name='temarios_estudiante'),
]