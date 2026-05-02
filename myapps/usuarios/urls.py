from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AuthUserViewSet,
    AuthTokenViewSet,
    LoginView,
    LogoutView,
    PerfilActualView,
    RegistroView,
    RolViewSet,
    UsuarioPerfilViewSet,
    UsuarioRolViewSet,
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioPerfilViewSet)
router.register(r'roles', RolViewSet)
router.register(r'usuario-roles', UsuarioRolViewSet)
router.register(r'tokens', AuthTokenViewSet, basename='tokens')
router.register(r'auth-users', AuthUserViewSet, basename='auth-users')

urlpatterns = [
    path('auth/registro/', RegistroView.as_view(), name='auth-registro'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', PerfilActualView.as_view(), name='auth-me'),
]

urlpatterns += router.urls
