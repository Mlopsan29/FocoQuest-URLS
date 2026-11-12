from django.urls import path, re_path
from . import views

# URL 2
urlpatterns = [
path('', views.index, name='index'),
path('psicologos/especialidad/<str:nombre_especialidad>/', views.psicologos_especialidad, name='psicologos_especialidad'),
]

