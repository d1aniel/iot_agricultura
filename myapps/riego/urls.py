from rest_framework.routers import DefaultRouter
from .views import RiegoViewSet

router = DefaultRouter()
router.register(r'commands', RiegoViewSet)

urlpatterns = router.urls