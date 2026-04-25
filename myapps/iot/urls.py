from rest_framework.routers import DefaultRouter

from .views import ActuadorViewSet, LecturaSensorViewSet, NodoIoTViewSet, SensorViewSet

router = DefaultRouter()
router.register(r'nodos-iot', NodoIoTViewSet)
router.register(r'sensores', SensorViewSet)
router.register(r'lecturas-sensor', LecturaSensorViewSet)
router.register(r'actuadores', ActuadorViewSet)

urlpatterns = router.urls
