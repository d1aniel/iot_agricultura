from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AuthTokenViewSet,
    ConfirmarRegistro2FAView,
    LoginView,
    LogoutView,
    PerfilActualView,
    RegistroView,
    RolViewSet,
    TwoFactorConfirmView,
    TwoFactorDisableView,
    TwoFactorSetupView,
    UsuarioPerfilViewSet,
    UsuarioRolViewSet,
    Verificar2FAView,
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioPerfilViewSet)
router.register(r'roles', RolViewSet)
router.register(r'usuario-roles', UsuarioRolViewSet)
router.register(r'tokens', AuthTokenViewSet, basename='tokens')

urlpatterns = [
    path('auth/registro/', RegistroView.as_view(), name='auth-registro'),
    path('auth/registro/confirmar-2fa/', ConfirmarRegistro2FAView.as_view(), name='auth-registro-confirmar-2fa'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/login/2fa/', Verificar2FAView.as_view(), name='auth-login-2fa'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', PerfilActualView.as_view(), name='auth-me'),
    path('auth/2fa/setup/', TwoFactorSetupView.as_view(), name='auth-2fa-setup'),
    path('auth/2fa/confirm/', TwoFactorConfirmView.as_view(), name='auth-2fa-confirm'),
    path('auth/2fa/disable/', TwoFactorDisableView.as_view(), name='auth-2fa-disable'),
]

urlpatterns += router.urls
