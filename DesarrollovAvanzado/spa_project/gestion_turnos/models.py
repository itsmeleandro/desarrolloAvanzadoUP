from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User

class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

class Profesional(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario.get_full_name()


class Horario(models.Model):
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE)
    fecha = models.DateField()  # Fecha del horario
    hora = models.TimeField()   # Hora del horario
    disponible = models.BooleanField(default=True)  # Si el horario está disponible

    def __str__(self):
        return f"{self.profesional} - {self.fecha} - {self.hora}"

from django.db import models

class Turno(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('pendiente', 'Pendiente'),
        ('cancelado', 'Cancelado'),
        ('cancelado_por_cliente', 'Cancelado por Cliente'),
        ('cancelado_por_profesional', 'Cancelado por Profesional'),
    ]
    id = models.AutoField(primary_key=True)  # Este es el campo por defecto

    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha_hora = models.CharField(max_length=20)  # Formato 'YYYY-MM-DDTHH:mm'
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='activo')

    def cancelar_por_cliente(self):
        """
        Cancela el turno por parte del cliente si falta más de 24 horas.
        """
        fecha_hora_obj = datetime.strptime(self.fecha_hora, "%Y-%m-%dT%H:%M")
        if fecha_hora_obj - timedelta(hours=24) <= datetime.now():
            raise ValueError("No puedes cancelar un turno con menos de 24 horas de antelación.")

        self.estado = 'cancelado_por_cliente'
        self.save()
        # Liberar el horario asociado
        self.liberar_horario()

    def cancelar_por_profesional(self):
        """
        Cancela el turno por parte del profesional. Intenta reasignar a otro profesional si es posible.
        """
        fecha_hora_obj = datetime.strptime(self.fecha_hora, "%Y-%m-%dT%H:%M")
        otros_profesionales = Profesional.objects.exclude(id=self.profesional.id)

        for profesional in otros_profesionales:
            if Horario.objects.filter(
                profesional=profesional,
                fecha=fecha_hora_obj.date(),
                hora=fecha_hora_obj.time(),
                disponible=True
            ).exists():
                # Reasignar el turno
                self.profesional = profesional
                self.save()
                Horario.objects.filter(
                    profesional=profesional,
                    fecha=fecha_hora_obj.date(),
                    hora=fecha_hora_obj.time()
                ).update(disponible=False)
                return f"Turno reasignado al profesional {profesional.usuario.get_full_name()}."

        # Si no es posible reasignar, cancelar el turno
        self.estado = 'cancelado_por_profesional'
        self.save()
        self.liberar_horario()
        return "El turno ha sido cancelado porque no había profesionales disponibles."

    def liberar_horario(self):
        """
        Libera el horario asociado al turno.
        """
        fecha, hora = self.fecha_hora.split('T')
        Horario.objects.filter(
            profesional=self.profesional,
            fecha=fecha,
            hora=hora
        ).update(disponible=True)

    def __str__(self):
        return f"{self.servicio.nombre} con {self.profesional.usuario.get_full_name()} el {self.fecha_hora} ({self.get_estado_display()})"