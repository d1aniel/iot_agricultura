from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DashboardView, FincaViewSet, OrganizacionViewSet, ParcelaViewSet

router = DefaultRouter()
router.register(r'organizaciones', OrganizacionViewSet)
router.register(r'fincas', FincaViewSet)
router.register(r'parcelas', ParcelaViewSet)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]

urlpatterns += router.urls
