from django.contrib import admin
from django.urls import path, include

from myapps.usuarios.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/users/login/', LoginView.as_view(), name='api-users-login'),
    path('api_usuarios/', include('myapps.usuarios.urls')),
    path('api_ubicacion/', include('myapps.ubicaciones.urls')),
    path('api_iot/', include('myapps.iot.urls')),
    path('api_riego/', include('myapps.riego.urls')),
    path('api_sistema/', include('myapps.sistema.urls')),
]
