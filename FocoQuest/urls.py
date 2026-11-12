from django.urls import path, re_path
from . import views

urlpatterns = [
# URL 5
path('psicologos/estadisticas/', views.psicologos_estadisticas, name='psicologos_estadisticas'),
]