from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import AuthToken, LoginChallenge, Rol, UsuarioPerfil, UsuarioRol


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioPerfil
        fields = '__all__'


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
    tiene_2fa = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'nombre_completo', 'is_active', 'tiene_2fa')
        read_only_fields = ('id', 'is_active', 'nombre_completo', 'tiene_2fa')

    def get_nombre_completo(self, obj):
        return obj.get_full_name()

    def get_tiene_2fa(self, obj):
        return False


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


class Verificar2FASerializer(serializers.Serializer):
    challenge_id = serializers.CharField()
    codigo = serializers.CharField(min_length=6, max_length=6)
    nombre_dispositivo = serializers.CharField(required=False, allow_blank=True, max_length=120)

    def validate_challenge_id(self, value):
        proposito = self.context.get('proposito', 'LOGIN')
        challenge = LoginChallenge.objects.select_related('usuario').filter(
            challenge_id=value,
            proposito=proposito,
        ).first()
        if not challenge or not challenge.esta_activo:
            raise serializers.ValidationError('Reto 2FA invalido o expirado.')
        self.context['challenge'] = challenge
        return value


class TwoFactorConfirmSerializer(serializers.Serializer):
    challenge_id = serializers.CharField()
    codigo = serializers.CharField(min_length=6, max_length=6)

    def validate_challenge_id(self, value):
        proposito = self.context.get('proposito', 'ACTIVAR_2FA')
        filtros = {
            'challenge_id': value,
            'proposito': proposito,
        }
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            filtros['usuario'] = request.user

        challenge = LoginChallenge.objects.select_related('usuario').filter(
            **filtros,
        ).first()
        if not challenge or not challenge.esta_activo:
            raise serializers.ValidationError('Reto 2FA invalido o expirado.')
        self.context['challenge'] = challenge
        return value


class AuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthToken
        fields = ('id', 'nombre_dispositivo', 'direccion_ip', 'fecha_creacion', 'ultimo_uso', 'fecha_expiracion', 'revocado')
        read_only_fields = fields
