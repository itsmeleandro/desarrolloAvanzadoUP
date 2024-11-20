from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('login')),  # Redirige a la vista de login
    path('admin/', admin.site.urls),
    path('turnos/', include('gestion_turnos.urls')),  # Asegúrate de que la URL de la app esté incluida
]
