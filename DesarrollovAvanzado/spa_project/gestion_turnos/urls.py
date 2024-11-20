from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cliente_dashboard/', views.cliente_dashboard, name='cliente_dashboard'),
    path('profesional_dashboard/', views.profesional_dashboard, name='profesional_dashboard'),
    path('horarios-disponibles/', views.horarios_disponibles, name='horarios_disponibles'),
    path('agendar/', views.agendar_turno, name='agendar_turno'),
    path('servicios-disponibles/', views.servicios_disponibles, name='servicios_disponibles'),  # Asegúrate de que esta línea está presente
    path('agendar/', views.agendar_turno, name='agendar_turno'),
    path('mis-turnos/', views.mis_turnos, name='mis_turnos'),
    path('cancelar/<int:turno_id>/', views.cancelar_turno, name='cancelar_turno'),  # Ruta correcta
    path('profesional_dashboard/', views.profesional_dashboard, name='profesional_dashboard'),
    path('profesionales-disponibles/', views.profesionales_disponibles, name='profesionales_disponibles'),
    path('mis-turnos-profesional/', views.mis_turnos_profesional, name='mis_turnos_profesional'),
    path('cancelar-profesional/<int:turno_id>/', views.cancelar_turno_profesional, name='cancelar_turno_profesional'),


]
