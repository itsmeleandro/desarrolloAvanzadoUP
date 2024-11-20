from django.core.management.base import BaseCommand
from gestion_turnos.models import Servicio, Profesional, Turno, Horario
from django.contrib.auth.models import User
from datetime import datetime, time, date


class Command(BaseCommand):
    help = "Populate the database with initial data"

    def handle(self, *args, **kwargs):
        # Crear Servicios
        servicio1 = Servicio.objects.create(
            nombre="Manicura", descripcion="Cuidado de uñas", precio=30.00
        )
        servicio2 = Servicio.objects.create(
            nombre="Pedicura", descripcion="Cuidado de pies", precio=35.00
        )
        servicio3 = Servicio.objects.create(
            nombre="Masajes", descripcion="Masajes relajantes y terapéuticos", precio=50.00
        )
        servicio4 = Servicio.objects.create(
            nombre="Alisado", descripcion="Tratamiento capilar", precio=70.00
        )
        self.stdout.write("Servicios creados.")
        # Crear Profesionales
        user1 = User.objects.create_user(
            username="ana_lopez",
            password="password123",
            first_name="Ana",
            last_name="Lopez",
            email="ana@example.com",
        )
        profesional1 = Profesional.objects.create(usuario=user1)

        user2 = User.objects.create_user(
            username="carlos_perez",
            password="password123",
            first_name="Carlos",
            last_name="Perez",
            email="carlos@example.com",
        )
        profesional2 = Profesional.objects.create(usuario=user2)

        user3 = User.objects.create_user(
            username="maria_gomez",
            password="password123",
            first_name="Maria",
            last_name="Gomez",
            email="maria@example.com",
        )
        profesional3 = Profesional.objects.create(usuario=user3)

        self.stdout.write("Profesionales creados.")

        # Crear Clientes
        cliente1 = User.objects.create_user(
            username="cliente1",
            password="cliente123",
            first_name="Juan",
            last_name="Martinez",
            email="juan@example.com",
        )
        cliente2 = User.objects.create_user(
            username="cliente2",
            password="cliente123",
            first_name="Lucia",
            last_name="Fernandez",
            email="lucia@example.com",
        )

        self.stdout.write("Clientes creados.")

      
        self.stdout.write("Turnos y horarios creados.")
        self.stdout.write(self.style.SUCCESS("Base de datos poblada con éxito."))
