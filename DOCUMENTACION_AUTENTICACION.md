# Documentacion de login, autenticacion y 2FA

## Resumen

Se agrego un flujo completo de autenticacion para la API Django REST Framework del proyecto:

- Registro de usuarios.
- Login con token de API.
- Logout con revocacion del token actual.
- Consulta del usuario autenticado.
- Proteccion global de rutas de la API.
- Autenticacion en dos pasos obligatoria con codigo OTP enviado al correo del usuario.
- Panel de administracion para revisar tokens, dispositivos 2FA y retos de login.

## Archivos modificados

- `agricultura_inteligente/settings.py`: configuracion global de DRF, expiracion de tokens y compatibilidad de PyMySQL.
- `myapps/usuarios/models.py`: modelos `AuthToken`, `TwoFactorDevice` y `LoginChallenge`.
- `myapps/usuarios/authentication.py`: autenticacion por header `Authorization`.
- `myapps/usuarios/email_otp.py`: generacion, envio y registro de codigos OTP por correo.
- `myapps/usuarios/serializers.py`: serializers para registro, login, usuario actual, tokens y 2FA.
- `myapps/usuarios/views.py`: endpoints de autenticacion, logout, perfil y 2FA.
- `myapps/usuarios/urls.py`: rutas publicas y protegidas de autenticacion.
- `myapps/usuarios/admin.py`: administracion de tokens, 2FA y retos.
- `myapps/usuarios/migrations/0002_auth_token_2fa.py`: migracion para las nuevas tablas.
- `myapps/usuarios/migrations/0003_email_otp.py`: migracion para OTP por email y expiracion.

## Nuevas tablas

### `auth_token_api`

Guarda tokens de API de forma segura mediante hash SHA-256. El token real solo se entrega una vez al hacer login.

Campos principales:

- `usuario`
- `token_hash`
- `nombre_dispositivo`
- `direccion_ip`
- `user_agent`
- `fecha_expiracion`
- `revocado`

### `two_factor_device`

Guarda si el usuario tiene 2FA por correo activado.

Campos principales:

- `usuario`
- `confirmado`
- `fecha_confirmacion`
- `ultimo_codigo_usado`

### `login_challenge`

Guarda retos temporales cuando un usuario con 2FA inicia sesion o activa/desactiva 2FA. Los codigos expiran en 15 minutos por defecto.

Campos principales:

- `usuario`
- `challenge_id`
- `codigo_hash`
- `proposito`
- `fecha_expiracion`
- `usado`

## Configuracion de correo

El envio de OTP usa SMTP. Las credenciales se leen desde variables de entorno para no dejar contrasenas dentro del codigo:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_correo@gmail.com'
EMAIL_HOST_PASSWORD = 'tu_contrasena_de_aplicacion'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

En este proyecto se configuraron mediante `python-decouple`, asi que puedes ponerlas en `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contrasena_de_aplicacion
DEFAULT_FROM_EMAIL=tu_correo@gmail.com
```

Con Gmail no se debe usar la contrasena normal de la cuenta. Se debe crear una contrasena de aplicacion desde la cuenta de Google.

## Proteccion de rutas

Se configuro DRF con permisos globales:

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

Esto hace que las rutas de la API requieran autenticacion por defecto. Las rutas de registro, login y verificacion 2FA quedan publicas explicitamente con `AllowAny`.

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
  "usuario": {
    "id": 1,
    "username": "usuario1",
    "email": "usuario@example.com",
    "tiene_2fa": false
  },
  "requiere_2fa": true,
  "challenge_id": "RETO_TEMPORAL",
  "expira_en": "2026-04-30T...",
  "mensaje": "Registro creado. Codigo de verificacion enviado al correo."
}
```

El usuario debe confirmar el codigo enviado al correo:

`POST /api_usuarios/auth/registro/confirmar-2fa/`

Body:

```json
{
  "challenge_id": "RETO_TEMPORAL",
  "codigo": "123456"
}
```

Si el codigo es correcto, el backend activa 2FA y devuelve el token de sesion.

### Login obligatorio con 2FA

`POST /api_usuarios/auth/login/`

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
  "requiere_2fa": true,
  "challenge_id": "RETO_TEMPORAL",
  "expira_en": "2026-04-30T...",
  "mensaje": "Codigo de verificacion enviado al correo.",
  "2fa_pendiente": false
}
```

El login nunca devuelve token directamente. Siempre envia un codigo al correo y exige validarlo.

### Activar 2FA

La activacion queda integrada al registro. Este endpoint se conserva para usuarios autenticados que aun no tengan 2FA confirmado.

`POST /api_usuarios/auth/2fa/setup/`

Header:

```http
Authorization: Token TU_TOKEN
```

Respuesta:

```json
{
  "challenge_id": "RETO_TEMPORAL",
  "expira_en": "2026-04-30T...",
  "confirmado": false,
  "mensaje": "Codigo de activacion enviado al correo."
}
```

3. Confirmar el codigo recibido por correo:

`POST /api_usuarios/auth/2fa/confirm/`

Body:

```json
{
  "challenge_id": "RETO_TEMPORAL",
  "codigo": "123456"
}
```

### Login con 2FA activo

Primera parte:

`POST /api_usuarios/auth/login/`

Respuesta:

```json
{
  "requiere_2fa": true,
  "challenge_id": "RETO_TEMPORAL",
  "expira_en": "2026-04-30T...",
  "mensaje": "Codigo de verificacion enviado al correo."
}
```

Segunda parte:

`POST /api_usuarios/auth/login/2fa/`

Body:

```json
{
  "challenge_id": "RETO_TEMPORAL",
  "codigo": "123456",
  "nombre_dispositivo": "Navegador principal"
}
```

Respuesta: igual al login normal, con token de API.

### Usuario actual

`GET /api_usuarios/auth/me/`

### Logout

`POST /api_usuarios/auth/logout/`

Revoca el token usado en la peticion.

### Desactivar 2FA

`POST /api_usuarios/auth/2fa/disable/`

La desactivacion esta bloqueada porque 2FA por correo es obligatorio para todos los usuarios.

### Listar tokens propios

`GET /api_usuarios/tokens/`

Permite ver las sesiones/tokens del usuario autenticado.

## Notas de seguridad

- Los tokens se guardan hasheados, no en texto plano.
- El token real solo se entrega al iniciar sesion.
- El logout revoca el token actual.
- Los retos 2FA por email expiran en 15 minutos.
- Los codigos OTP no se guardan en texto plano; se guarda su hash SHA-256.
- Cada reto queda marcado como usado despues de una verificacion correcta.
- El correo es obligatorio para registrarse.
- El login siempre requiere codigo OTP por correo antes de entregar token.
- La desactivacion de 2FA esta bloqueada por politica del sistema.

## Comandos necesarios

Aplicar migraciones:

```bash
python manage.py migrate
```

Verificar el proyecto:

```bash
python manage.py check
```

## Validacion realizada

Se ejecuto:

```bash
python manage.py check
```

Resultado: sin errores.

Tambien se verifico que no hay migraciones pendientes con:

```bash
python manage.py makemigrations --check --dry-run
```

Resultado: sin cambios pendientes. El entorno local no pudo comprobar la historia de migraciones contra MySQL remoto por restricciones de red del sandbox.
