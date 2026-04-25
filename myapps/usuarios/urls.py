from rest_framework.routers import DefaultRouter

from .views import RolViewSet, UsuarioPerfilViewSet, UsuarioRolViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioPerfilViewSet)
router.register(r'roles', RolViewSet)
router.register(r'usuario-roles', UsuarioRolViewSet)

urlpatterns = router.urls
