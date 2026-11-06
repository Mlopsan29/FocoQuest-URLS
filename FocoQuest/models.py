from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

# 1. Estudiante

class Estudiante(models.Model):
    OBJETIVOS = [
        ('Opositor', 'Opositor'),
        ('Universitario', 'Universitario'),
        ('Bachillerato/FP', 'Bachillerato/FP'),
    ]
    objetivo = models.CharField(max_length=20, choices=OBJETIVOS, default='Universitario')
    nivel = models.IntegerField(default=1)
    xp = models.IntegerField(default=0, help_text="Puntos de experiencia acumulados")
    racha_actual = models.IntegerField(default=0)
    racha_maxima = models.IntegerField(default=0)
    ultimo_dia_activo = models.DateField(null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    biografia = models.TextField(blank=True)
    hora_recordatorio = models.TimeField(null=True, blank=True)
    notificaciones_push = models.BooleanField(default=False)
    acepta_tratamiento_salud = models.BooleanField(default=False)
    actualizado = models.DateTimeField(auto_now=True)

    # OneToOne: cada estudiante pertenece a un único User y cada User tiene como máximo un perfil de estudiante

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='estudiante')

    # ManyToMany con tabla intermedia (ObtencionLogro, con atributos extra)

    logros = models.ManyToManyField('Logro', through='ObtencionLogro', related_name='estudiantes')

    # ManyToMany: un estudiante puede tener varios psicólogos favoritos y un psicólogo ser favorito de varios estudiantes

    psicologos_favoritos = models.ManyToManyField('Psicologo', blank=True, related_name='seguidores_estudiantes')

    def __str__(self):
        return f"Estudiante {self.user.username}"


# 2. Trabajador

class Trabajador(models.Model):
    OBJETIVOS = [
        ('Productividad', 'Productividad'),
        ('Formación continua', 'Formación continua'),
        ('Certificación', 'Certificación'),
    ]
    objetivo = models.CharField(max_length=20, choices=OBJETIVOS, default='Productividad')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    biografia = models.TextField(blank=True)
    acepta_tratamiento_salud = models.BooleanField(default=False)
    ultimo_dia_activo = models.DateField(null=True, blank=True)

    # OneToOne: cada trabajador pertenece a un único User

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trabajador')

    # ManyToMany: un trabajador puede tener varios psicólogos favoritos y un psicólogo ser favorito de varios trabajadores

    psicologos_favoritos = models.ManyToManyField('Psicologo', blank=True, related_name='seguidores_trabajadores')

    def __str__(self):
        return f"Trabajador {self.user.username}"


# 3. Administrador

class Administrador(models.Model):
    permisos = models.TextField(blank=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)

    # OneToOne: cada administrador pertenece a un único User

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='administrador')

    def __str__(self):
        return f"Administrador {self.user.username}"


# 4. Mascota

class Mascota(models.Model):
    ETAPAS = [
        ('Huevo', 'Huevo'),
        ('Larva', 'Larva'),
        ('Adulta', 'Adulta'),
        ('Resplandeciente', 'Resplandeciente'),
    ]
    etapa = models.CharField(max_length=20, choices=ETAPAS, default='Huevo')
    energia = models.IntegerField(default=100)
    color = models.CharField(max_length=7, default='#FFB547')
    fecha_adopcion = models.DateField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    # OneToOne: cada estudiante tiene una única mascota

    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name='mascota')

    def __str__(self):
        return f"Mascota ({self.etapa})"


# 5. Temario

class Temario(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3DBE9B')
    fecha_examen = models.DateField(null=True, blank=True)
    horas_objetivo = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    activa = models.BooleanField(default=True)

    # ManyToOne: un estudiante tiene muchos temarios

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='temarios')

    def __str__(self):
        return self.nombre


# 6. SesionEstudio (se abre con "Comenzar día" y se cierra con "Finalizar día")

class SesionEstudio(models.Model):
    inicio = models.DateTimeField(default=timezone.now)
    fin = models.DateTimeField(null=True, blank=True)
    minutos_estudiados = models.IntegerField(default=0)
    pomodoros_completados = models.IntegerField(default=0)
    xp_ganada = models.IntegerField(default=0)
    notas = models.TextField(blank=True)

    # ManyToOne: un temario tiene muchas sesiones de estudio

    temario = models.ForeignKey(Temario, on_delete=models.CASCADE, related_name='sesiones')

    def __str__(self):
        return f"{self.temario} - {self.inicio:%d/%m/%Y}"


# 7. RegistroAnimo (cuestionario que salta al pulsar "Finalizar día")

class RegistroAnimo(models.Model):
    ESTADOS = [
        ('Tranquilo', 'Tranquilo'),
        ('Motivado', 'Motivado'),
        ('Agobiado', 'Agobiado'),
        ('Exhausto', 'Exhausto'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS)
    nivel_estres = models.IntegerField(default=5, help_text="De 1 a 10")
    horas_sueno = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    comentario = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    # OneToOne: cada sesión tiene un único registro de ánimo

    sesion = models.OneToOneField(SesionEstudio, on_delete=models.CASCADE, related_name='registro_animo')

    def __str__(self):
        return self.estado


# 8. MetodoEstudio (cada método se concreta en una Tarjeta, un Esquema o un Resumen)

class MetodoEstudio(models.Model):
    TIPOS = [
        ('Tarjeta', 'Tarjeta'),
        ('Esquema', 'Esquema'),
        ('Resumen', 'Resumen'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPOS)
    titulo = models.CharField(max_length=100)

    # ManyToOne: un temario tiene muchos métodos de estudio

    temario = models.ForeignKey(Temario, on_delete=models.CASCADE, related_name='metodos')

    def __str__(self):
        return f"{self.titulo} ({self.tipo})"


# 9. Tarjeta (flashcard con repetición espaciada)

class Tarjeta(models.Model):
    anverso = models.TextField(help_text="Pregunta o concepto")
    reverso = models.TextField(help_text="Respuesta o definición")
    caja = models.IntegerField(default=1)
    facilidad = models.FloatField(default=2.5)
    intervalo_dias = models.IntegerField(default=1)
    proximo_repaso = models.DateField(default=datetime.date.today)

    # OneToOne: cada tarjeta es la concreción de un método de estudio

    metodo = models.OneToOneField(MetodoEstudio, on_delete=models.CASCADE, related_name='tarjeta')

    def __str__(self):
        return self.anverso[:40]


# 10. Esquema

class Esquema(models.Model):
    TIPOS_ESQUEMA = [
        ('Mapa mental', 'Mapa mental'),
        ('Cuadro sinóptico', 'Cuadro sinóptico'),
        ('Diagrama de flujo', 'Diagrama de flujo'),
    ]
    contenido = models.TextField()
    tipo_esquema = models.CharField(max_length=20, choices=TIPOS_ESQUEMA, default='Mapa mental')
    imagen_url = models.URLField(blank=True)

    # OneToOne: cada esquema es la concreción de un método de estudio

    metodo = models.OneToOneField(MetodoEstudio, on_delete=models.CASCADE, related_name='esquema')

    def __str__(self):
        return f"Esquema ({self.tipo_esquema})"


# 11. Resumen

class Resumen(models.Model):
    texto = models.TextField()
    fuente = models.CharField(max_length=200, blank=True)

    # OneToOne: cada resumen es la concreción de un método de estudio

    metodo = models.OneToOneField(MetodoEstudio, on_delete=models.CASCADE, related_name='resumen')

    def __str__(self):
        return self.texto[:40]


# 12. Especialidad

class Especialidad(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    descripcion = models.TextField(blank=True)
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


# 13. Psicologo (directorio de especialistas)

class Psicologo(models.Model):
    MODALIDADES = [
        ('Online', 'Online'),
        ('Presencial', 'Presencial'),
        ('Ambas', 'Ambas'),
    ]
    nombre_completo = models.CharField(max_length=120)
    numero_colegiado = models.CharField("nº de colegiado", max_length=20, unique=True)
    descripcion = models.TextField()
    email = models.EmailField(max_length=254, unique=True)
    telefono = models.CharField(max_length=16, blank=True)
    web = models.URLField(blank=True)
    modalidad = models.CharField(max_length=15, choices=MODALIDADES, default='Online')
    precio_sesion = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fecha_alta = models.DateField(auto_now_add=True)

    # OneToOne: la cuenta de User con la que el psicólogo edita su ficha (opcional)

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ficha_psicologo')

    # ManyToMany: un psicólogo tiene varias especialidades y una especialidad la tienen varios psicólogos

    especialidades = models.ManyToManyField(Especialidad, related_name='psicologos')

    def __str__(self):
        return self.nombre_completo


# 14. Logro

class Logro(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=80)
    descripcion = models.TextField()
    xp_recompensa = models.IntegerField(default=50)
    icono_url = models.URLField(blank=True)

    def __str__(self):
        return self.nombre


# 15. ObtencionLogro (tabla intermedia Estudiante y Logro, con atributos extra)

class ObtencionLogro(models.Model):
    fecha_obtencion = models.DateTimeField(auto_now_add=True)
    progreso = models.IntegerField(default=0, help_text="Porcentaje de 0 a 100")
    destacado = models.BooleanField(default=False)
    notificado = models.BooleanField(default=False)

    # ManyToOne: un estudiante puede obtener muchos logros

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='obtenciones')

    # ManyToOne: un logro puede ser obtenido por muchos estudiantes

    logro = models.ForeignKey(Logro, on_delete=models.CASCADE, related_name='obtenciones')

    def __str__(self):
        return f"{self.estudiante} - {self.logro}"
