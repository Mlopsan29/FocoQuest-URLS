# FocoQuest · URLs, vistas y QuerySets

## Flujo de ramas de Git

* `master`: rama principal. Solo recibe la fusión de la rama de la tarea cuando está todo terminado.
* `URLS`: rama de esta tarea.
* `URL1` … `URL10`: una rama por cada URL. Cada una se crea desde `URLS` y se fusiona de nuevo en `URLS`
  (`git merge --no-ff`).
* Al terminar, `URLS` se fusiona en `master`.

## Páginas de error personalizadas

Definidas en `mysite/urls.py` (`handler400`, `handler403`, `handler404`, `handler500`) con sus vistas en
`FocoQuest/views.py` y sus plantillas en `FocoQuest/templates/FocoQuest/errores/`.

| Error | Plantilla | Cómo provocarlo (enlaces también en el index) |
|---|---|---|
| 400 Petición incorrecta | `errores/400.html` | `/probar-error/400/` (la vista lanza `BadRequest`) |
| 403 Acceso prohibido | `errores/403.html` | `/probar-error/403/` (la vista lanza `PermissionDenied`) |
| 404 Página no encontrada | `errores/404.html` | cualquier URL inexistente, p. ej. `/esta-pagina-no-existe/` |
| 500 Error del servidor | `errores/500.html` | `/probar-error/500/` (la vista lanza una excepción) |

## Explicación de lo investigado
* **`Q` y el operador `|` (filtro con OR)**: `filter(a=1, b=2)` combina las condiciones con AND. Para un OR se
  envuelve cada condición en un objeto `Q` (`from django.db.models import Q`) y se unen con `|`:
  `filter(Q(a=1) | Q(b=2))`. Se usa en la URL 4.
* **`aggregate()`**: calcula un único valor sobre todas las filas de un queryset usando funciones de
  agregación (`Count`, `Avg`, `Min`, `Max`, `Sum`, de `django.db.models`). Devuelve un **diccionario**
  (`{'total': 7, 'precio_medio': ...}`), no un queryset. En SQL equivale a `SELECT COUNT(..), AVG(..) ... FROM ...`.
  Se usa en la URL 5.

## URLs de la aplicación

### URL 1 · `estudiante/<int:id_estudiante>/temarios/`

* **Nombre de la URL:** `temarios_estudiante` · **Ejemplo:** `/estudiante/1/temarios/`
* **Vista:** `temarios_estudiante` en `FocoQuest/views.py` · **Plantilla:** `FocoQuest/templates/FocoQuest/estudiante/temarios.html`
* **Qué hace:** Muestra todos los temarios de un estudiante (por su id) con los datos completos del estudiante, de su usuario y de su mascota.
* **Requisitos que cumple:**
  * Parámetro **entero** (`<int:id_estudiante>`)
  * Relación **ManyToOne** (Temario → Estudiante)
  * Relación **OneToOne** (Estudiante → User y Estudiante → Mascota, esta última inversa)
  * `order_by`
  * Consulta optimizada con `select_related` (1 sola consulta)
* **Consultas a la base de datos por petición:** 1
* **QuerySet:**

```python
Temario.objects.select_related("estudiante__user", "estudiante__mascota").filter(estudiante=id_estudiante).order_by("fecha_examen")
```

* **SQL equivalente:**

```sql
SELECT t.*, e.*, u.*, m.*
FROM FocoQuest_temario t
  INNER JOIN FocoQuest_estudiante e ON t.estudiante_id = e.id
  INNER JOIN auth_user u ON e.user_id = u.id
  LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
WHERE t.estudiante_id = :id_estudiante
ORDER BY t.fecha_examen ASC;
```

### URL 2 · `psicologos/especialidad/<str:nombre_especialidad>/`

* **Nombre de la URL:** `psicologos_especialidad` · **Ejemplo:** `/psicologos/especialidad/Ansiedad/`
* **Vista:** `psicologos_especialidad` en `FocoQuest/views.py` · **Plantilla:** `FocoQuest/templates/FocoQuest/psicologo/por_especialidad.html`
* **Qué hace:** Lista los psicólogos que tienen una especialidad (texto recibido por la URL) con toda su información, todas sus especialidades y quién los tiene como favoritos.
* **Requisitos que cumple:**
  * Parámetro **string** (`<str:nombre_especialidad>`)
  * Relación **ManyToMany** (Psicólogo ↔ Especialidad)
  * Uso de **relación reversa** (`seguidores_estudiantes`, `seguidores_trabajadores`, M2M inversas por `related_name`)
  * Relación **OneToOne** (Psicólogo → User, opcional)
  * `order_by`
  * Consulta optimizada: `select_related` + `prefetch_related` (6 consultas fijas, sin importar cuántos psicólogos haya)
* **Consultas a la base de datos por petición:** 6
* **QuerySet:**

```python
Psicologo.objects.select_related("user").prefetch_related("especialidades", "seguidores_estudiantes__user", "seguidores_trabajadores__user").filter(especialidades__nombre__icontains=nombre_especialidad).distinct().order_by("nombre_completo")
```

* **SQL equivalente:**

```sql
SELECT DISTINCT p.*, u.*
FROM FocoQuest_psicologo p
  INNER JOIN FocoQuest_psicologo_especialidades pe ON p.id = pe.psicologo_id
  INNER JOIN FocoQuest_especialidad esp ON pe.especialidad_id = esp.id
  LEFT OUTER JOIN auth_user u ON p.user_id = u.id
WHERE esp.nombre LIKE '%:nombre_especialidad%'
ORDER BY p.nombre_completo ASC;
-- + 5 consultas de prefetch_related (especialidades, estudiantes seguidores, sus usuarios,
--   trabajadores seguidores y sus usuarios), todas con WHERE ... IN (...)
```

### URL 3 · `psicologos/<str:modalidad>/<int:precio_maximo>/`

* **Nombre de la URL:** `psicologos_modalidad_precio` · **Ejemplo:** `/psicologos/Online/50/`
* **Vista:** `psicologos_modalidad_precio` en `FocoQuest/views.py` · **Plantilla:** `FocoQuest/templates/FocoQuest/psicologo/por_modalidad_precio.html`
* **Qué hace:** Muestra los psicólogos de una modalidad cuyo precio por sesión no supera un máximo, del más barato al más caro.
* **Requisitos que cumple:**
  * **Dos parámetros** en la URL (`<str:modalidad>` y `<int:precio_maximo>`)
  * Parámetro **entero** y parámetro **string**
  * **Filtro con AND** (`filter(modalidad=..., precio_sesion__lte=...)`)
  * Relación **ManyToMany** (Psicólogo ↔ Especialidad) y **OneToOne** (Psicólogo → User)
  * `order_by`
  * Consulta optimizada: `select_related` + `prefetch_related` (2 consultas)
* **Consultas a la base de datos por petición:** 2
* **QuerySet:**

```python
Psicologo.objects.select_related("user").prefetch_related("especialidades").filter(modalidad=modalidad, precio_sesion__lte=precio_maximo).order_by("precio_sesion")
```

* **SQL equivalente:**

```sql
SELECT p.*, u.*
FROM FocoQuest_psicologo p
  LEFT OUTER JOIN auth_user u ON p.user_id = u.id
WHERE p.modalidad = :modalidad AND p.precio_sesion <= :precio_maximo
ORDER BY p.precio_sesion ASC;
-- + 1 consulta de prefetch_related para las especialidades (WHERE pe.psicologo_id IN (...))
```

### URL 4 · `estudiantes/destacados/`

* **Nombre de la URL:** `estudiantes_destacados` · **Ejemplo:** `/estudiantes/destacados/`
* **Vista:** `estudiantes_destacados` en `FocoQuest/views.py` · **Plantilla:** `FocoQuest/templates/FocoQuest/estudiante/destacados.html`
* **Qué hace:** Lista los estudiantes de nivel alto o con racha larga, con su usuario, su mascota y todos sus logros (con el progreso de cada uno).
* **Requisitos que cumple:**
  * **Filtro con OR** (objetos `Q` unidos con `|`)
  * Relación **ManyToMany con tabla intermedia** (Estudiante ↔ Logro a través de ObtencionLogro)
  * Relación **OneToOne** (Estudiante → User, Estudiante → Mascota)
  * `order_by`
  * Consulta optimizada: `select_related` + `prefetch_related` (3 consultas)
* **Consultas a la base de datos por petición:** 3
* **QuerySet:**

```python
Estudiante.objects.select_related("user", "mascota").prefetch_related("obtenciones__logro").filter(Q(nivel__gte=8) | Q(racha_actual__gte=10)).order_by("-nivel")
```

* **SQL equivalente:**

```sql
SELECT e.*, u.*, m.*
FROM FocoQuest_estudiante e
  INNER JOIN auth_user u ON e.user_id = u.id
  LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
WHERE (e.nivel >= 8 OR e.racha_actual >= 10)
ORDER BY e.nivel DESC;
-- + 2 consultas de prefetch_related: obtenciones (WHERE estudiante_id IN (...)) y logros (WHERE id IN (...))
```

### URL 5 · `psicologos/estadisticas/`

* **Nombre de la URL:** `psicologos_estadisticas` · **Ejemplo:** `/psicologos/estadisticas/`
* **Vista:** `psicologos_estadisticas` en `FocoQuest/views.py` · **Plantilla:** `FocoQuest/templates/FocoQuest/psicologo/estadisticas.html`
* **Qué hace:** Calcula con `aggregate` el nº de psicólogos con precio, el precio medio, mínimo y máximo, cuenta los que no tienen precio y lista los psicólogos con todo su detalle.
* **Requisitos que cumple:**
  * **Filtro con `aggregate`** (`Count`, `Avg`, `Min`, `Max`)
  * **Filtro con None** (`precio_sesion=None` y `precio_sesion__isnull=False`)
  * Relación **ManyToMany** (Psicólogo ↔ Especialidad) y **OneToOne** (Psicólogo → User)
  * `order_by`
  * Consulta optimizada: `select_related` + `prefetch_related` (4 consultas en total)
* **Consultas a la base de datos por petición:** 4
* **QuerySet:**

```python
Psicologo.objects.filter(precio_sesion__isnull=False).aggregate(total=Count("id"), precio_medio=Avg("precio_sesion"), precio_minimo=Min("precio_sesion"), precio_maximo=Max("precio_sesion"))
```

* **SQL equivalente:**

```sql
SELECT COUNT(p.id) AS total, AVG(p.precio_sesion) AS precio_medio,
       MIN(p.precio_sesion) AS precio_minimo, MAX(p.precio_sesion) AS precio_maximo
FROM FocoQuest_psicologo p
WHERE p.precio_sesion IS NOT NULL;
-- Además: SELECT COUNT(*) FROM FocoQuest_psicologo WHERE precio_sesion IS NULL;
-- y el listado (select_related + prefetch_related, ORDER BY precio_sesion ASC)
```

### URL 6 · `estudiantes/ranking/`

* **Nombre de la URL:** `ranking_estudiantes` · **Ejemplo:** `/estudiantes/ranking/`
* **Vista:** `ranking_estudiantes` en `FocoQuest/views.py` · **Plantilla:** `FocoQuest/templates/FocoQuest/estudiante/ranking.html`
* **Qué hace:** Muestra el top 3 de estudiantes por XP con su usuario, su mascota y todos sus temarios.
* **Requisitos que cumple:**
  * **Limit** (`[:3]` → `LIMIT 3`)
  * `order_by` descendente (`-xp`)
  * Relación **OneToOne** (Estudiante → User y Mascota)
  * Relación **ManyToOne** inversa (Estudiante → Temarios)
  * Consulta optimizada: `select_related` + `prefetch_related` (2 consultas)
* **Consultas a la base de datos por petición:** 2
* **QuerySet:**

```python
Estudiante.objects.select_related("user", "mascota").prefetch_related("temarios").order_by("-xp")[:3]
```

* **SQL equivalente:**

```sql
SELECT e.*, u.*, m.*
FROM FocoQuest_estudiante e
  INNER JOIN auth_user u ON e.user_id = u.id
  LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
ORDER BY e.xp DESC
LIMIT 3;
-- + SELECT t.* FROM FocoQuest_temario t WHERE t.estudiante_id IN (ids de los 3 estudiantes);
```

### URL 7 · `^estudiantes/examen/(?P<anio>[0-9]{4})/$  (re_path)`

* **Nombre de la URL:** `estudiantes_examen_anio` · **Ejemplo:** `/estudiantes/examen/2027/`
* **Vista:** `estudiantes_examen_anio` en `FocoQuest/views.py` · **Plantilla:** `FocoQuest/templates/FocoQuest/estudiante/examenes_anio.html`
* **Qué hace:** Muestra los estudiantes que tienen algún temario con examen en el año indicado, con su usuario, su mascota y todos sus temarios.
* **Requisitos que cumple:**
  * **URL con `re_path`** (expresión regular de 4 dígitos)
  * **Relación reversa** (`temarios__fecha_examen__year` desde Estudiante)
  * Relación **ManyToOne** inversa (Estudiante → Temarios) y **OneToOne** (User y Mascota)
  * `order_by` por un campo de la tabla relacionada (`user__username`)
  * Consulta optimizada: `select_related` + `prefetch_related` + `distinct` (2 consultas)
* **Consultas a la base de datos por petición:** 2
* **QuerySet:**

```python
Estudiante.objects.select_related("user", "mascota").prefetch_related("temarios").filter(temarios__fecha_examen__year=anio).distinct().order_by("user__username")
```

* **SQL equivalente:**

```sql
SELECT DISTINCT e.*, u.*, m.*
FROM FocoQuest_estudiante e
  INNER JOIN FocoQuest_temario t ON e.id = t.estudiante_id
  INNER JOIN auth_user u ON e.user_id = u.id
  LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
WHERE t.fecha_examen BETWEEN :anio-01-01 AND :anio-12-31
ORDER BY u.username ASC;
-- + SELECT t.* FROM FocoQuest_temario t WHERE t.estudiante_id IN (...);
```

### URL 8 · `estudiantes/sin-logros/`

* **Nombre de la URL:** `estudiantes_sin_logros` · **Ejemplo:** `/estudiantes/sin-logros/`
* **Vista:** `estudiantes_sin_logros` en `FocoQuest/views.py` · **Plantilla:** `FocoQuest/templates/FocoQuest/estudiante/sin_logros.html`
* **Qué hace:** Lista los estudiantes sin ningún logro, con su usuario, su mascota y sus psicólogos favoritos (con usuario y especialidades).
* **Requisitos que cumple:**
  * **Filtro con None en una tabla intermedia** (`filter(obtenciones=None)` sobre ObtencionLogro)
  * Relación **ManyToMany** (Estudiante ↔ Psicólogo favoritos; Psicólogo ↔ Especialidad)
  * Relación **OneToOne** (User, Mascota y User del psicólogo)
  * `order_by` por campo de tabla relacionada
  * Consulta optimizada: `select_related` + `prefetch_related` (4 consultas)
* **Consultas a la base de datos por petición:** 4
* **QuerySet:**

```python
Estudiante.objects.select_related("user", "mascota").prefetch_related("psicologos_favoritos__user", "psicologos_favoritos__especialidades").filter(obtenciones=None).order_by("user__username")
```

* **SQL equivalente:**

```sql
SELECT e.*, u.*, m.*
FROM FocoQuest_estudiante e
  LEFT OUTER JOIN FocoQuest_obtencionlogro o ON e.id = o.estudiante_id
  INNER JOIN auth_user u ON e.user_id = u.id
  LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
WHERE o.id IS NULL
ORDER BY u.username ASC;
-- + 3 consultas de prefetch_related (psicólogos favoritos, sus usuarios y sus especialidades)
```

### URL 9 · `logro/<int:id_logro>/estudiantes/`

* **Nombre de la URL:** `estudiantes_logro` · **Ejemplo:** `/logro/2/estudiantes/`
* **Vista:** `estudiantes_logro` en `FocoQuest/views.py` · **Plantilla:** `FocoQuest/templates/FocoQuest/logro/estudiantes.html`
* **Qué hace:** Muestra quién ha obtenido un logro (por su id) con el progreso de cada estudiante y todos los datos del logro, del estudiante, de su usuario y de su mascota.
* **Requisitos que cumple:**
  * Parámetro **entero** (`<int:id_logro>`)
  * **Tabla intermedia** del ManyToMany (ObtencionLogro) consultada con dos relaciones **ManyToOne**
  * Relación **OneToOne** (Estudiante → User y Mascota)
  * `order_by` descendente
  * Consulta optimizada con `select_related` (1 sola consulta)
* **Consultas a la base de datos por petición:** 1
* **QuerySet:**

```python
ObtencionLogro.objects.select_related("estudiante__user", "estudiante__mascota", "logro").filter(logro=id_logro).order_by("-progreso")
```

* **SQL equivalente:**

```sql
SELECT o.*, l.*, e.*, u.*, m.*
FROM FocoQuest_obtencionlogro o
  INNER JOIN FocoQuest_estudiante e ON o.estudiante_id = e.id
  INNER JOIN auth_user u ON e.user_id = u.id
  LEFT OUTER JOIN FocoQuest_mascota m ON m.estudiante_id = e.id
  INNER JOIN FocoQuest_logro l ON o.logro_id = l.id
WHERE o.logro_id = :id_logro
ORDER BY o.progreso DESC;
```

### URL 10 · `trabajadores/favoritos/`

* **Nombre de la URL:** `trabajadores_favoritos` · **Ejemplo:** `/trabajadores/favoritos/`
* **Vista:** `trabajadores_favoritos` en `FocoQuest/views.py` · **Plantilla:** `FocoQuest/templates/FocoQuest/trabajador/favoritos.html`
* **Qué hace:** Lista los trabajadores con su usuario y sus psicólogos favoritos (con el usuario y las especialidades de cada psicólogo).
* **Requisitos que cumple:**
  * Relación **ManyToMany** (Trabajador ↔ Psicólogo favoritos; Psicólogo ↔ Especialidad)
  * Relación **OneToOne** (Trabajador → User y Psicólogo → User)
  * `order_by` por campo de tabla relacionada (`user__last_name`)
  * Consulta optimizada: `select_related` + `prefetch_related` (4 consultas)
* **Consultas a la base de datos por petición:** 4
* **QuerySet:**

```python
Trabajador.objects.select_related("user").prefetch_related("psicologos_favoritos__user", "psicologos_favoritos__especialidades").order_by("user__last_name")
```

* **SQL equivalente:**

```sql
SELECT t.*, u.*
FROM FocoQuest_trabajador t
  INNER JOIN auth_user u ON t.user_id = u.id
ORDER BY u.last_name ASC;
-- + 3 consultas de prefetch_related (psicólogos favoritos, sus usuarios y sus especialidades)
```

## Resumen del cumplimiento de requisitos

| Requisito de la tarea | Dónde se cumple |
|---|---|
| 10 URLs con vistas, QuerySet y plantillas | URLs 1 a 10 (sección 7) |
| Una rama por URL fusionada en la rama de la tarea | Ramas `URL1`…`URL10` fusionadas en `URLS` (sección 4) |
| Datos entre tablas **ManyToMany**, **OneToOne** y **ManyToOne** | ManyToMany: URLs 2, 3, 4, 5, 8, 10 · OneToOne: todas (User, Mascota) · ManyToOne: URLs 1, 6, 7, 9 |
| Comentario en cada vista explicando lo que hace | Todas las vistas de `FocoQuest/views.py` |
| Todas las URLs detalladas en el README con sus requisitos | Sección 7 |
| Página de error personalizada para los 4 tipos de error | Sección 5 (400, 403, 404, 500) |
| URLs que funcionan y muestran resultados | Todos los enlaces del index devuelven datos del fixture |
| Mostrar siempre toda la información de los modelos relacionados | Las plantillas muestran todos los campos de cada modelo relacionado (salvo la contraseña del `User`, por seguridad) |
| Queries optimizadas | `select_related` y `prefetch_related` en todas; nº de consultas fijo por URL (indicado en cada sección) |
| SQL comentado en cada QuerySet | Comentario `# SELECT ...` dentro de cada vista y bloque SQL en el README |
| `re_path` | URL 7 |
| Dos parámetros | URL 3 (`<str:modalidad>/<int:precio_maximo>`) |
| Parámetro entero | URLs 1, 3 y 9 |
| Parámetro string | URLs 2 y 3 |
| Filtro con **AND** | URL 3 |
| Filtro con **OR** | URL 4 (`Q(...) \| Q(...)`) |
| **aggregate** | URL 5 (`Count`, `Avg`, `Min`, `Max`) |
| **Relación reversa** | URL 2 (`seguidores_estudiantes`, `seguidores_trabajadores`) y URL 7 (`temarios__fecha_examen__year`) |
| **order_by** | Todas las URLs de listado |
| **Limit** | URL 6 (`[:3]`) |
| Filtro con **None** en tabla intermedia | URL 8 (`filter(obtenciones=None)` sobre ObtencionLogro); URL 5 usa además `precio_sesion=None` |
| Index con acceso a todas las URLs | `/` (`FocoQuest/templates/FocoQuest/index.html`) |
| Archivos que no se suben a Git | `.gitignore`|
| Fixture con datos de prueba | `FocoQuest/fixtures/datos_iniciales.json`|
| Proyecto en modo producción | `DEBUG = False`|
| Se puede descargar de Git, cargar el fixture y probar las URLs |

