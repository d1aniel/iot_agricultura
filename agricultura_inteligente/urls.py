from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # API de tu sistema IoT
    path('api/', include('myapps.devices.urls')),
    path('api/', include('myapps.sensores.urls')),
    path('api/', include('myapps.riego.urls')),
]