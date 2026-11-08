from django.urls import path, re_path
from . import views

urlpatterns = [
    # Index: desde aquí se accede a todas las URLs
    path('', views.index, name='index'),

    # URL 1
    path('estudiante/<int:id_estudiante>/temarios/', views.temarios_estudiante, name='temarios_estudiante'),
]