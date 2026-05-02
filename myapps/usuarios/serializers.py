from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import AuthToken, Rol, UsuarioPerfil, UsuarioRol
from .permissions import usuario_tiene_rol_administrativo


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', read_only=True)
    email = serializers.EmailField(source='usuario.email', read_only=True)
    first_name = serializers.CharField(source='usuario.first_name', read_only=True)
    last_name = serializers.CharField(source='usuario.last_name', read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    organizacion_nombre = serializers.CharField(source='organizacion.nombre', read_only=True)

    class Meta:
        model = UsuarioPerfil
        fields = (
            'id',
            'usuario',
            'username',
            'email',
            'first_name',
            'last_name',
            'nombre_completo',
            'organizacion',
            'organizacion_nombre',
            'telefono',
            'estado',
            'ultimo_acceso',
            'fecha_creacion',
        )
        read_only_fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'nombre_completo',
            'organizacion_nombre',
            'ultimo_acceso',
            'fecha_creacion',
        )

    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class UsuarioRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioRol
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    es_administrador_o_auditor = serializers.SerializerMethodField()

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
            'es_administrador_o_auditor',
        )
        read_only_fields = ('id', 'is_active', 'nombre_completo', 'roles', 'es_administrador_o_auditor')

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
