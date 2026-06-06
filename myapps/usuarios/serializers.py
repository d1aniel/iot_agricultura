from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from rest_framework import serializers
import json
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

from .models import AuthToken, Rol, UsuarioPerfil, UsuarioRol
from .permissions import usuario_tiene_rol_activo, usuario_tiene_rol_administrativo


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', required=False, max_length=150)
    email = serializers.EmailField(source='usuario.email', required=False)
    first_name = serializers.CharField(source='usuario.first_name', required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(source='usuario.last_name', required=False, allow_blank=True, max_length=150)
    nombre_completo = serializers.SerializerMethodField()
    organizacion_nombre = serializers.CharField(source='organizacion.nombre', read_only=True)
    nuevo_username = serializers.CharField(write_only=True, required=False, max_length=150)
    nuevo_email = serializers.EmailField(write_only=True, required=False)
    nuevos_nombres = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=150)
    nuevos_apellidos = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=150)
    password_temporal = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = UsuarioPerfil
        fields = (
            'id',
            'usuario',
            'nuevo_username',
            'nuevo_email',
            'nuevos_nombres',
            'nuevos_apellidos',
            'password_temporal',
            'username',
            'email',
            'first_name',
            'last_name',
            'nombre_completo',
            'organizacion',
            'organizacion_nombre',
            'telefono',
            'estado',
            'requiere_cambio_password',
            'ultimo_acceso',
            'fecha_creacion',
        )
        read_only_fields = (
            'nombre_completo',
            'organizacion_nombre',
            'requiere_cambio_password',
            'ultimo_acceso',
            'fecha_creacion',
        )
        extra_kwargs = {
            'usuario': {'required': False},
        }

    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username

    def validate(self, attrs):
        if self.instance:
            usuario_data = attrs.get('usuario', {})
            username = usuario_data.get('username')
            email = usuario_data.get('email')
            if username and User.objects.exclude(pk=self.instance.usuario_id).filter(username=username).exists():
                raise serializers.ValidationError({'username': 'Este nombre de usuario ya existe.'})
            if email and User.objects.exclude(pk=self.instance.usuario_id).filter(email=email).exists():
                raise serializers.ValidationError({'email': 'Este correo ya esta registrado.'})
            return attrs

        username = attrs.get('nuevo_username')
        email = attrs.get('nuevo_email')
        password = attrs.get('password_temporal')

        if not username or not email or not password:
            raise serializers.ValidationError('Usuario, correo y contrasena temporal son obligatorios.')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'nuevo_username': 'Este nombre de usuario ya existe.'})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'nuevo_email': 'Este correo ya esta registrado.'})
        return attrs

    def create(self, validated_data):
        username = validated_data.pop('nuevo_username')
        email = validated_data.pop('nuevo_email')
        first_name = validated_data.pop('nuevos_nombres', '')
        last_name = validated_data.pop('nuevos_apellidos', '')
        password = validated_data.pop('password_temporal')
        validated_data.pop('usuario', None)

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        perfil = UsuarioPerfil.objects.create(
            usuario=user,
            requiere_cambio_password=True,
            **validated_data,
        )
        enviar_correo_usuario_creado(user, password)
        return perfil

    def update(self, instance, validated_data):
        password = validated_data.pop('password_temporal', None)
        usuario_data = validated_data.pop('usuario', {})
        validated_data.pop('nuevo_username', None)
        validated_data.pop('nuevo_email', None)
        validated_data.pop('nuevos_nombres', None)
        validated_data.pop('nuevos_apellidos', None)

        if usuario_data:
            user = instance.usuario
            for field in ('username', 'email', 'first_name', 'last_name'):
                if field in usuario_data:
                    setattr(user, field, usuario_data[field])
            user.save(update_fields=[field for field in ('username', 'email', 'first_name', 'last_name') if field in usuario_data])

        if password:
            instance.usuario.set_password(password)
            instance.usuario.save(update_fields=['password'])
            instance.requiere_cambio_password = True

        return super().update(instance, validated_data)


def enviar_correo_usuario_creado(user, password_temporal):
    if not user.email or not settings.RESEND_API_KEY:
        return

    login_url = f'{settings.FRONTEND_URL.rstrip("/")}/login'
    nombre = user.get_full_name() or user.username
    payload = {
        'from': settings.RESEND_FROM_EMAIL,
        'to': user.email,
        'subject': 'Tu cuenta de Riego IoT fue creada',
        'html': (
            f'<p>Hola {nombre},</p>'
            '<p>Un administrador creo tu cuenta en el sistema de riego inteligente.</p>'
            f'<p><strong>Usuario:</strong> {user.username}</p>'
            f'<p><strong>Contrasena temporal:</strong> {password_temporal}</p>'
            f'<p>Ingresa aqui: <a href="{login_url}">{login_url}</a></p>'
            '<p>Al iniciar sesion se te pedira cambiar esta contrasena temporal.</p>'
        ),
    }
    req = urlrequest.Request(
        'https://api.resend.com/emails',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {settings.RESEND_API_KEY}',
            'Content-Type': 'application/json',
            'User-Agent': 'agricultura-inteligente-backend/1.0',
        },
        method='POST',
    )
    try:
        urlrequest.urlopen(req, timeout=10)
    except HTTPError as exc:
        detalle = exc.read().decode('utf-8', errors='replace')
        print(
            'Error enviando correo de usuario creado: '
            f'status={exc.code} from={settings.RESEND_FROM_EMAIL} to={user.email} body={detalle}'
        )
    except URLError as exc:
        print(f'Error enviando correo de usuario creado: {exc}')


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class UsuarioRolSerializer(serializers.ModelSerializer):
    asignado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = UsuarioRol
        fields = (
            'id',
            'usuario',
            'rol',
            'fecha_asignacion',
            'asignado_por',
            'asignado_por_nombre',
            'estado',
        )
        read_only_fields = ('fecha_asignacion', 'asignado_por', 'asignado_por_nombre')

    def get_asignado_por_nombre(self, obj):
        if not obj.asignado_por:
            return ''

        return str(obj.asignado_por)


class UserSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    tiene_rol_activo = serializers.SerializerMethodField()
    es_administrador_o_auditor = serializers.SerializerMethodField()
    requiere_cambio_password = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'nombre_completo',
            'is_active',
            'roles',
            'tiene_rol_activo',
            'es_administrador_o_auditor',
            'requiere_cambio_password',
        )
        read_only_fields = ('id', 'is_active', 'nombre_completo', 'roles', 'tiene_rol_activo', 'es_administrador_o_auditor', 'requiere_cambio_password')

    def get_nombre_completo(self, obj):
        return obj.get_full_name()

    def get_roles(self, obj):
        perfil = getattr(obj, 'perfil_iot', None)
        if not perfil:
            return []

        return list(
            perfil.roles
            .filter(estado='ACTIVO', rol__estado='ACTIVO')
            .values_list('rol__nombre', flat=True)
        )

    def get_es_administrador_o_auditor(self, obj):
        return usuario_tiene_rol_administrativo(obj)

    def get_tiene_rol_activo(self, obj):
        return usuario_tiene_rol_activo(obj)

    def get_requiere_cambio_password(self, obj):
        perfil = getattr(obj, 'perfil_iot', None)
        return bool(perfil and perfil.requiere_cambio_password)


class CambiarPasswordTemporalSerializer(serializers.Serializer):
    password_actual = serializers.CharField(write_only=True)
    nueva_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_password_actual(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contrasena actual no es correcta.')
        return value


class OlvidePasswordSerializer(serializers.Serializer):
    identificador = serializers.CharField()


class RestablecerPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    nueva_password = serializers.CharField(write_only=True, validators=[validate_password])


class RegistroSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    telefono = serializers.CharField(required=False, allow_blank=True, max_length=30)
    organizacion = serializers.PrimaryKeyRelatedField(
        queryset=UsuarioPerfil._meta.get_field('organizacion').remote_field.model.objects.all(),
        required=False,
        allow_null=True,
    )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este nombre de usuario ya existe.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este correo ya esta registrado.')
        return value

    def create(self, validated_data):
        telefono = validated_data.pop('telefono', '')
        organizacion = validated_data.pop('organizacion', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        UsuarioPerfil.objects.create(usuario=user, telefono=telefono, organizacion=organizacion)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    nombre_dispositivo = serializers.CharField(required=False, allow_blank=True, max_length=120)

    def validate(self, attrs):
        user = authenticate(username=attrs.get('username'), password=attrs.get('password'))
        if not user:
            raise serializers.ValidationError('Credenciales invalidas.')
        if not user.is_active:
            raise serializers.ValidationError('Usuario inactivo.')

        perfil = UsuarioPerfil.objects.filter(usuario=user).first()
        if perfil and perfil.estado != 'ACTIVO':
            raise serializers.ValidationError('El perfil de usuario no esta activo.')

        attrs['user'] = user
        return attrs


class AuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthToken
        fields = ('id', 'nombre_dispositivo', 'direccion_ip', 'fecha_creacion', 'ultimo_uso', 'fecha_expiracion', 'revocado')
        read_only_fields = fields
