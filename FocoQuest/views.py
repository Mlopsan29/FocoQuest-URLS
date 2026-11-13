from django.shortcuts import render

# Create your views here.
# Error 400: petición incorrecta.
def mi_error_400(request, exception=None):
    return render(request, 'FocoQuest/errores/400.html', None, None, 400)


# Error 403: acceso prohibido.
def mi_error_403(request, exception=None):
    return render(request, 'FocoQuest/errores/403.html', None, None, 403)


# Error 404: página no encontrada.
def mi_error_404(request, exception=None):
    return render(request, 'FocoQuest/errores/404.html', None, None, 404)


# Error 500: error interno del servidor.
def mi_error_500(request, exception=None):
    return render(request, 'FocoQuest/errores/500.html', None, None, 500)