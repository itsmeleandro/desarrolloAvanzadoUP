# Generated by Django 5.1.3 on 2024-11-19 07:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_turnos', '0002_horario_delete_agenda'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='horario',
            name='hora_fin',
        ),
    ]
