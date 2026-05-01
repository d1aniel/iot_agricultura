from django.utils import timezone
from rest_framework import authentication, exceptions

from myapps.usuarios.models import AuthToken


class TokenAuthentication(authentication.BaseAuthentication):
    keyword = 'Token'

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode('utf-8')
        if not header:
            return None

        partes = header.split()
        if len(partes) != 2 or partes[0] not in (self.keyword, 'Bearer'):
            return None

        token_hash = AuthToken.hash_token(partes[1])
        token_api = AuthToken.objects.select_related('usuario').filter(token_hash=token_hash).first()

        if not token_api or not token_api.esta_activo:
            raise exceptions.AuthenticationFailed('Token invalido o expirado.')

        usuario = token_api.usuario
        if not usuario.is_active:
            raise exceptions.AuthenticationFailed('Usuario inactivo.')

        token_api.ultimo_uso = timezone.now()
        token_api.save(update_fields=['ultimo_uso'])
        return usuario, token_api
