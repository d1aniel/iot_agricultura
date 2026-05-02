from django.db import transaction
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from myapps.sistema.models import AuditoriaSistema
from myapps.usuarios.models import AuthToken, Rol, UsuarioPerfil, UsuarioRol
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
            'detail': 'API de Agricultura Inteligente. Usa el frontend para iniciar sesion o envia JSON a los endpoints de autenticacion.',
            'login': {
                'method': 'POST',
                'url': '/api/users/login/',
                'body': {
                    'username': 'usuario',
                    'password': 'contrasena',
                    'nombre_dispositivo': 'Navegador web',
                },
            },
            'registro': {
                'method': 'POST',
                'url': '/api/users/register/',
                'body': {
                    'username': 'usuario',
                    'password': 'contrasena',
                    'email': 'correo@example.com',
                    'first_name': 'Nombre',
                    'last_name': 'Apellido',
                    'telefono': '3000000000',
                },
            },
        })


class UsuarioPerfilViewSet(viewsets.ModelViewSet):
    queryset = UsuarioPerfil.objects.all()
    serializer_class = UsuarioPerfilSerializer
    permission_classes = [IsAuthenticated]


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAdminUser]


class UsuarioRolViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRol.objects.all()
    serializer_class = UsuarioRolSerializer
    permission_classes = [IsAdminUser]


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
