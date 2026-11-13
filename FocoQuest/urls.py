from django.urls import path, re_path
from . import views

urlpatterns = [
   # --- URLs de prueba para provocar a mano los errores personalizados ---
path('probar-error/400/', views.probar_error_400, name='probar_error_400'),
path('probar-error/403/', views.probar_error_403, name='probar_error_403'),
path('probar-error/500/', views.probar_error_500, name='probar_error_500'),
]