import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from spa_project import settings
from .models import Servicio, Profesional, Turno, Horario
from datetime import datetime, timedelta


class AutenticacionTestCase(TestCase):
    """
    Pruebas relacionadas con la autenticación.
    """
    def setUp(self):
        self.client = Client()

    def test_redireccion_a_login(self):
        """
        Verifica que usuarios no autenticados sean redirigidos al login.
        """
        response = self.client.get(reverse("cliente_dashboard"))
        self.assertEqual(response.status_code, 302)  # Confirmar redirección
        self.assertTrue(settings.LOGIN_URL in response.url)  # Usar LOGIN_URL


class CancelacionTurnosTestCase(TestCase):
    def setUp(self):
        self.cliente = User.objects.create_user(username="cliente", password="test123")
        self.profesional = User.objects.create_user(username="profesional", password="test123")
        self.servicio = Servicio.objects.create(nombre="Corte de cabello", precio=100)
        self.profesional_obj = Profesional.objects.create(usuario=self.profesional)

        self.turno_future = Turno.objects.create(
            cliente=self.cliente,
            profesional=self.profesional_obj,
            servicio=self.servicio,
            fecha_hora=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
            estado="activo",
        )
        self.client = Client()

    def test_cliente_no_puede_cancelar_sin_autenticacion(self):
        """
        Verifica que un cliente no autenticado no pueda cancelar un turno.
        """
        cancel_url = reverse("cancelar_turno", kwargs={"turno_id": self.turno_future.id})
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, 302)  # Confirmar redirección
        self.assertIn(settings.LOGIN_URL, response.url.split('?')[0])  # Confirmar redirección a login


class ValidacionFormularioTestCase(TestCase):
    def setUp(self):
        self.cliente = User.objects.create_user(username="cliente", password="test123")
        self.servicio = Servicio.objects.create(nombre="Corte de cabello", precio=100)
        self.profesional = User.objects.create_user(username="profesional", password="test123")
        self.profesional_obj = Profesional.objects.create(usuario=self.profesional)
        self.client = Client()

    def test_campo_faltante_en_formulario(self):
        """
        Verifica que el sistema devuelva un error si faltan campos obligatorios.
        """
        agendar_url = reverse("agendar_turno")
        payload = {
            "profesional_id": "",
            "fecha_hora": "2024-11-20T10:00",
            "servicio_id": "",
        }
        response = self.client.post(
            agendar_url,
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)  # Confirmar error por datos faltantes
        self.assertIn("Faltan datos necesarios.", response.json().get("message", ""))

class ValidacionFormularioTestCase(TestCase):
    """
    Pruebas para la validación de formularios.
    """
    def setUp(self):
        # Crear datos mínimos para pruebas
        self.cliente = User.objects.create_user(username="cliente", password="test123")
        self.servicio = Servicio.objects.create(nombre="Corte de cabello", precio=100)
        self.profesional = User.objects.create_user(username="profesional", password="test123")
        self.profesional_obj = Profesional.objects.create(usuario=self.profesional)
        self.client = Client()

    def test_campo_faltante_en_formulario(self):
        """
        Verifica que el sistema devuelva un error si faltan campos obligatorios.
        """
        agendar_url = reverse("agendar_turno")
        payload = {
            "profesional_id": "",
            "fecha_hora": "2024-11-20T10:00",
            "servicio_id": "",
        }
        response = self.client.post(
            agendar_url,
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)  # Confirmar error por datos faltantes
        self.assertIn("Faltan datos necesarios.", response.json().get("message", ""))


class TurnosTestCase(TestCase):
    """
    Pruebas generales para los turnos y visualización de horarios.
    """
    def setUp(self):
        # Crear usuario cliente y profesional
        self.cliente = User.objects.create_user(username="cliente", password="test123")
        self.profesional = User.objects.create_user(username="profesional", password="test123")

        # Crear servicio, profesional y turnos
        self.servicio = Servicio.objects.create(nombre="Corte de cabello", precio=100)
        self.profesional_obj = Profesional.objects.create(usuario=self.profesional)
        self.horario = Horario.objects.create(
            profesional=self.profesional_obj,
            fecha=datetime.now().date(),
            hora=(datetime.now() + timedelta(hours=1)).time(),
            disponible=False
        )
        self.turno_future = Turno.objects.create(
            cliente=self.cliente,
            profesional=self.profesional_obj,
            servicio=self.servicio,
            fecha_hora=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
            estado="activo",
        )
        self.turno_past = Turno.objects.create(
            cliente=self.cliente,
            profesional=self.profesional_obj,
            servicio=self.servicio,
            fecha_hora=(datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
            estado="activo",
        )
        self.client = Client()

    def test_cliente_no_puede_cancelar_turno_pasado(self):
        """
        Verifica que un cliente no pueda cancelar un turno pasado.
        """
        self.client.login(username="cliente", password="test123")
        cancel_url = reverse("cancelar_turno", kwargs={"turno_id": self.turno_past.id})
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, 400)  # Código de solicitud incorrecta
        self.assertIn("No puedes cancelar un turno pasado.", response.json()["message"])

    def test_cliente_puede_cancelar_turno_futuro(self):
        """
        Verifica que un cliente pueda cancelar un turno futuro.
        """
        self.client.login(username="cliente", password="test123")
        cancel_url = reverse("cancelar_turno", kwargs={"turno_id": self.turno_future.id})
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Turno cancelado con éxito.", response.json()["message"])

    def test_visualizacion_correcta_de_horarios(self):
        """
        Verifica que los horarios disponibles y los días se muestren correctamente.
        """
        self.client.login(username="profesional", password="test123")
        horarios_url = reverse("horarios_disponibles") + f"?profesional_id={self.profesional_obj.id}"
        response = self.client.get(horarios_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("dias", data)
        self.assertIsInstance(data["dias"], list)
