from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from myapps.sistema.models import AuditoriaSistema
from myapps.usuarios.models import AuthToken, Rol, UsuarioPerfil, UsuarioRol
from myapps.usuarios.permissions import IsAdministradorOrAuditor
from myapps.usuarios.serializers import (
    AuthTokenSerializer,
    LoginSerializer,
    RegistroSerializer,
    RolSerializer,
    UserSerializer,
    UsuarioPerfilSerializer,
    UsuarioRolSerializer,
)


class ApiRootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'detail': 'API de Agricultura Inteligente. Las rutas de modulos estan protegidas por token.',
            'seguridad': {
                'mensaje_sin_token': 'Las credenciales de autenticacion no se proveyeron.',
                'header_requerido': 'Authorization: Token <token>',
                'tambien_acepta': 'Authorization: Bearer <token>',
                'nota_evaluacion': 'Para validar los modulos, inicia sesion con las credenciales entregadas y usa el token recibido en cada peticion.',
            },
            'login': {
                'method': 'POST',
                'url': '/api_usuarios/auth/login/',
                'alias': '/api/users/login/',
                'body': {
                    'username': 'usuario',
                    'password': 'contrasena',
                    'nombre_dispositivo': 'Navegador web',
                },
            },
            'registro': {
                'method': 'POST',
                'url': '/api_usuarios/auth/registro/',
                'alias': '/api/users/register/',
                'body': {
                    'username': 'usuario',
                    'password': 'contrasena',
                    'email': 'correo@example.com',
                    'first_name': 'Nombre',
                    'last_name': 'Apellido',
                    'telefono': '3000000000',
                },
            },
            'modulos_protegidos': {
                'usuarios': '/api_usuarios/usuarios/',
                'roles': '/api_usuarios/roles/',
                'usuario_roles': '/api_usuarios/usuario-roles/',
                'tokens': '/api_usuarios/tokens/',
                'auth_users': '/api_usuarios/auth-users/',
                'organizaciones': '/api_ubicacion/organizaciones/',
                'fincas': '/api_ubicacion/fincas/',
                'parcelas': '/api_ubicacion/parcelas/',
                'nodos_iot': '/api_iot/nodos-iot/',
                'sensores': '/api_iot/sensores/',
                'lecturas_sensor': '/api_iot/lecturas-sensor/',
                'actuadores': '/api_iot/actuadores/',
                'estados_riego': '/api_riego/estados-riego/',
                'reglas_riego': '/api_riego/reglas-riego/',
                'comandos_riego': '/api_riego/comandos-riego/',
                'respuestas_comando': '/api_riego/respuestas-comando/',
                'alertas_sistema': '/api_sistema/alertas-sistema/',
                'auditorias_sistema': '/api_sistema/auditorias-sistema/',
            },
            'ejemplo_uso': {
                'paso_1': 'POST /api_usuarios/auth/login/ con username y password.',
                'paso_2': 'Copia el token de la respuesta.',
                'paso_3': 'GET /api_ubicacion/fincas/ con Authorization: Token <token>.',
            },
        })


class UsuarioPerfilViewSet(viewsets.ModelViewSet):
    queryset = UsuarioPerfil.objects.select_related('usuario', 'organizacion').all()
    serializer_class = UsuarioPerfilSerializer
    permission_classes = [IsAdministradorOrAuditor]


class AuthUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdministradorOrAuditor]


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAdministradorOrAuditor]


class UsuarioRolViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRol.objects.select_related('usuario__usuario', 'rol', 'asignado_por__usuario').all()
    serializer_class = UsuarioRolSerializer
    permission_classes = [IsAdministradorOrAuditor]

    def perform_create(self, serializer):
        asignador = UsuarioPerfil.objects.filter(usuario=self.request.user).first()
        serializer.save(asignado_por=asignador)


def obtener_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def registrar_auditoria_login(user, request, descripcion):
    perfil = UsuarioPerfil.objects.filter(usuario=user).first()
    AuditoriaSistema.objects.create(
        usuario=perfil,
        tabla_afectada='auth',
        accion='INICIAR_SESION',
        descripcion=descripcion,
        direccion_ip=obtener_ip(request),
    )


def crear_respuesta_token(user, request, nombre_dispositivo=None, status_code=status.HTTP_200_OK):
    token = AuthToken.crear_token(
        usuario=user,
        nombre_dispositivo=nombre_dispositivo,
        direccion_ip=obtener_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )
    perfil = UsuarioPerfil.objects.filter(usuario=user).first()
    if perfil:
        perfil.ultimo_acceso = timezone.now()
        perfil.save(update_fields=['ultimo_acceso'])
    registrar_auditoria_login(user, request, 'Inicio de sesion exitoso')
    return Response({
        'token': token,
        'tipo': 'Token',
        'usuario': UserSerializer(user).data,
    }, status=status_code)


class RegistroView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'detail': 'Envia una peticion POST con JSON para registrar un usuario.',
            'body': {
                'username': 'usuario',
                'password': 'contrasena',
                'email': 'correo@example.com',
                'first_name': 'Nombre',
                'last_name': 'Apellido',
                'telefono': '3000000000',
            },
        })

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = serializer.save()
        return crear_respuesta_token(user, request, status_code=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'detail': 'Envia una peticion POST con JSON para iniciar sesion.',
            'body': {
                'username': 'usuario',
                'password': 'contrasena',
                'nombre_dispositivo': 'Navegador web',
            },
        })

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return crear_respuesta_token(user, request, serializer.validated_data.get('nombre_dispositivo'))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if isinstance(request.auth, AuthToken):
            request.auth.revocado = True
            request.auth.save(update_fields=['revocado'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerfilActualView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class AuthTokenViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuthTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AuthToken.objects.filter(usuario=self.request.user).order_by('-fecha_creacion')
