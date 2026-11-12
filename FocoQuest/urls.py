from django.urls import path, re_path
from . import views

urlpatterns = [
    path('estudiantes/sin-logros/', views.estudiantes_sin_logros, name='estudiantes_sin_logros'),

]
