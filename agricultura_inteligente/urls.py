from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('myapps.usuarios.urls')),
    path('api/', include('myapps.ubicaciones.urls')),
    path('api/', include('myapps.iot.urls')),
    path('api/', include('myapps.riego.urls')),
    path('api/', include('myapps.sistema.urls')),
]
