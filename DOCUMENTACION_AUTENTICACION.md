# Documentacion de autenticacion

## Resumen

La API usa autenticacion por token para proteger las rutas privadas.

- Registro de usuarios.
- Login con token de API.
- Logout con revocacion del token actual.
- Consulta del usuario autenticado.
- Proteccion global de rutas de la API.
- Panel de administracion para revisar tokens.

## Archivos principales

- `agricultura_inteligente/settings.py`: configuracion global de DRF y expiracion de tokens.
- `myapps/usuarios/models.py`: modelo `AuthToken`.
- `myapps/usuarios/authentication.py`: autenticacion por header `Authorization`.
- `myapps/usuarios/serializers.py`: serializers para registro, login, usuario actual y tokens.
- `myapps/usuarios/views.py`: endpoints de autenticacion, logout y perfil.
- `myapps/usuarios/urls.py`: rutas publicas y protegidas de autenticacion.
- `myapps/usuarios/admin.py`: administracion de tokens.

## Tabla `auth_token_api`

Guarda tokens de API de forma segura mediante hash SHA-256. El token real solo se entrega una vez al registrarse o iniciar sesion.

Campos principales:

- `usuario`
- `token_hash`
- `nombre_dispositivo`
- `direccion_ip`
- `user_agent`
- `fecha_expiracion`
- `revocado`

## Proteccion de rutas

DRF esta configurado con permisos globales:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'myapps.usuarios.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

Esto hace que las rutas de la API requieran autenticacion por defecto. Las rutas de registro y login quedan publicas explicitamente con `AllowAny`.

## Uso de tokens

El cliente debe enviar el token en cada peticion protegida:

```http
Authorization: Token TU_TOKEN
```

Tambien se acepta:

```http
Authorization: Bearer TU_TOKEN
```

## Endpoints

Base: `/api_usuarios/`

### Registro

`POST /api_usuarios/auth/registro/`

Body:

```json
{
  "username": "usuario1",
  "password": "ClaveSegura123",
  "email": "usuario@example.com",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "telefono": "3000000000"
}
```

Respuesta:

```json
{
  "token": "TOKEN_GENERADO",
  "tipo": "Token",
  "usuario": {
    "id": 1,
    "username": "usuario1",
    "email": "usuario@example.com",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "nombre_completo": "Nombre Apellido",
    "is_active": true
  }
}
```

### Login

`POST /api_usuarios/auth/login/`

Tambien esta disponible el alias compatible:

`POST /api/users/login/`

Body:

```json
{
  "username": "usuario1",
  "password": "ClaveSegura123",
  "nombre_dispositivo": "Navegador principal"
}
```

Respuesta:

```json
{
  "token": "TOKEN_GENERADO",
  "tipo": "Token",
  "usuario": {
    "id": 1,
    "username": "usuario1",
    "email": "usuario@example.com",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "nombre_completo": "Nombre Apellido",
    "is_active": true
  }
}
```

### Usuario actual

`GET /api_usuarios/auth/me/`

### Logout

`POST /api_usuarios/auth/logout/`

Revoca el token usado en la peticion.

### Listar tokens propios

`GET /api_usuarios/tokens/`

Permite ver las sesiones/tokens del usuario autenticado.

## Notas de seguridad

- Los tokens se guardan hasheados, no en texto plano.
- El token real solo se entrega al registrarse o iniciar sesion.
- El logout revoca el token actual.
- La expiracion de tokens se controla con `AUTH_TOKEN_EXPIRATION_DAYS`.

## Comandos necesarios

Aplicar migraciones:

```bash
python manage.py migrate
```

Verificar el proyecto:

```bash
python manage.py check
```
