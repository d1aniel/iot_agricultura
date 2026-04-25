from rest_framework.routers import DefaultRouter

from .views import AlertaSistemaViewSet, AuditoriaSistemaViewSet

router = DefaultRouter()
router.register(r'alertas-sistema', AlertaSistemaViewSet)
router.register(r'auditorias-sistema', AuditoriaSistemaViewSet)

urlpatterns = router.urls
