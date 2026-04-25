from rest_framework.routers import DefaultRouter

from .views import (
    ComandoRiegoViewSet,
    EstadoRiegoViewSet,
    ReglaRiegoAutomaticoViewSet,
    RespuestaComandoViewSet,
)

router = DefaultRouter()
router.register(r'estados-riego', EstadoRiegoViewSet)
router.register(r'reglas-riego', ReglaRiegoAutomaticoViewSet)
router.register(r'comandos-riego', ComandoRiegoViewSet)
router.register(r'respuestas-comando', RespuestaComandoViewSet)

urlpatterns = router.urls
