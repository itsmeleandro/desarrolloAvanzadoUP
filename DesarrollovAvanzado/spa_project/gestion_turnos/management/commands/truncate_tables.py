from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Trunca todas las tablas en la base de datos."

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = OFF;")
            tables = connection.introspection.table_names()
            for table in tables:
                self.stdout.write(f"Truncando tabla: {table}")
                cursor.execute(f"DELETE FROM {table};")
            cursor.execute("PRAGMA foreign_keys = ON;")
        self.stdout.write(self.style.SUCCESS("Todas las tablas han sido truncadas."))
