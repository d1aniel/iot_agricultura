from rest_framework.routers import DefaultRouter
from .views import SensorViewSet

router = DefaultRouter()
router.register(r'readings', SensorViewSet)

urlpatterns = router.urls