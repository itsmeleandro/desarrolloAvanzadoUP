
from datetime import datetime, timedelta
from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.shortcuts import redirect

from django.core.serializers.json import DjangoJSONEncoder
from .models import Servicio, Profesional, Turno, Horario
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone



def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            try:
                profesional = Profesional.objects.get(usuario=user)
                return redirect("profesional_dashboard")
            except Profesional.DoesNotExist:
                return redirect("cliente_dashboard")
        else:
            error = "Credenciales inválidas. Por favor, intenta nuevamente."

    return render(request, "login.html", {"error": error})



@login_required
def cliente_dashboard(request):
    # Convertimos el QuerySet a una lista de diccionarios serializables
    servicios = list(Servicio.objects.values("id", "nombre", "precio"))
    profesionales = list(Profesional.objects.values("id", "usuario__first_name", "usuario__last_name"))

    # Si el formulario fue enviado, creamos el turno
    if request.method == "POST":
        profesional_id = request.POST.get("profesional")
        servicio_id = request.POST.get("servicio")
        fecha_hora = request.POST.get("fecha_hora")

        if profesional_id and servicio_id and fecha_hora:
            profesional = Profesional.objects.get(id=profesional_id)
            servicio = Servicio.objects.get(id=servicio_id)

            # Crear el turno
            Turno.objects.create(
                cliente=request.user,
                profesional=profesional,
                servicio=servicio,
                fecha_hora=fecha_hora,
            )
            return render(
                request,
                "cliente_dashboard.html",
                {
                    "servicios": json.dumps(servicios, cls=DjangoJSONEncoder),
                    "profesionales": profesionales,
                    "success": "Turno agendado con éxito",
                },
            )

    return render(
        request,
        "cliente_dashboard.html",
        {
            "servicios": json.dumps(servicios, cls=DjangoJSONEncoder),
            "profesionales": profesionales,
        },
    )

@login_required
def profesional_dashboard(request):
    """
    Vista para el profesional. Muestra solo los turnos activos o pendientes.
    """
    profesional = get_object_or_404(Profesional, usuario=request.user)

    # Filtrar turnos que están activos o pendientes
    turnos = Turno.objects.filter(profesional=profesional).exclude(
        estado__in=['cancelado', 'cancelado_por_cliente', 'cancelado_por_profesional']
    ).order_by('fecha_hora')

    # Procesar los turnos para separar fecha y hora
    turnos_list = []
    for turno in turnos:
        if 'T' in turno.fecha_hora:
            fecha, hora = turno.fecha_hora.split('T')
        else:
            fecha, hora = turno.fecha_hora, "Hora no especificada"
        
        turnos_list.append({
            "id": turno.id,
            "cliente": turno.cliente.get_full_name(),
            "servicio": turno.servicio.nombre,
            "fecha": fecha,
            "hora": hora,
            "estado": turno.estado,
        })

    return render(request, 'profesional_dashboard.html', {'turnos': turnos_list})

def logout_view(request):
    logout(request)
    return redirect('login')

def horarios_disponibles(request):
    profesional_id = request.GET.get("profesional_id")
    fecha = request.GET.get("fecha")  # Obtener la fecha seleccionada

    if not profesional_id:
        return JsonResponse({"error": "Falta el id del profesional."}, status=400)

    profesional = get_object_or_404(Profesional, id=profesional_id)

    # Definir las posibles globalmente (9:00 AM a 4:00 PM)
    horas_posibles = [datetime.strptime(f"{h:02}:00", "%H:%M").time() for h in range(9, 17)]

    if fecha:  # Mostrar horas disponibles de un día específico
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()

        # Filtrar horarios ocupados del profesional para esa fecha
        horarios_ocupados = Horario.objects.filter(
            profesional=profesional,
            fecha=fecha_obj,
            disponible=False  # Solo los horarios ocupados (no disponibles)
        ).values_list("hora", flat=True)

        # Determinar las horas disponibles (no ocupadas)
        horas_disponibles = [hora for hora in horas_posibles if hora not in horarios_ocupados]

        return JsonResponse({
            "horas": [{"hora": hora.strftime("%H:%M"), "disponible": hora not in horarios_ocupados} for hora in horas_posibles]
        })

    else:  # Mostrar los días disponibles (próximos 10 días)
        hoy = datetime.now().date()
        limite = hoy + timedelta(days=10)

        dias_disponibles = []
        for i in range(11):  # Hoy + 10 días
            dia_actual = hoy + timedelta(days=i)
            horarios_del_dia = Horario.objects.filter(
                profesional=profesional,
                fecha=dia_actual
            ).values_list("hora", flat=True)

            # Si no están todas las horas ocupadas
            horas_disponibles = [hora for hora in horas_posibles if hora not in horarios_del_dia]
            if horas_disponibles:
                dias_disponibles.append({"fecha": dia_actual.strftime("%Y-%m-%d")})

        return JsonResponse({"dias": dias_disponibles})

    

def servicios_disponibles(request):
    servicios = Servicio.objects.all().values("id", "nombre", "precio")
    return JsonResponse({"servicios": list(servicios)})


@login_required
def cliente_dashboard(request):
    # Obtener los turnos agendados para el cliente
    turnos = Turno.objects.filter(cliente=request.user).order_by('fecha_hora')

    # Convertir los servicios y profesionales a listas de diccionarios serializables
    servicios = list(Servicio.objects.values("id", "nombre", "precio"))
    profesionales = list(Profesional.objects.values("id", "usuario__first_name", "usuario__last_name"))

    if request.method == "POST":
        # Lógica para crear un nuevo turno
        profesional_id = request.POST.get("profesional")
        servicio_id = request.POST.get("servicio")
        fecha_hora = request.POST.get("fecha_hora")

        if profesional_id and servicio_id and fecha_hora:
            profesional = Profesional.objects.get(id=profesional_id)
            servicio = Servicio.objects.get(id=servicio_id)

            # Crear el turno
            Turno.objects.create(
                cliente=request.user,
                profesional=profesional,
                servicio=servicio,
                fecha_hora=fecha_hora,
            )

            return render(
                request,
                "cliente_dashboard.html",
                {
                    "servicios": json.dumps(servicios, cls=DjangoJSONEncoder),
                    "profesionales": profesionales,
                    "turnos": turnos,  # Mostrar los turnos agendados
                    "success": "Turno agendado con éxito",
                },
            )

    return render(
        request,
        "cliente_dashboard.html",
        {
            "servicios": json.dumps(servicios, cls=DjangoJSONEncoder),
            "profesionales": profesionales,
            "turnos": turnos,  # Mostrar los turnos agendados
        },
    )


@csrf_exempt
def agendar_turno(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        profesional_id = data.get('profesional_id')
        fecha_hora = data.get('fecha_hora')
        servicio_id = data.get('servicio_id')

        # Validar que todos los campos necesarios están presentes
        if not (profesional_id and fecha_hora and servicio_id):
            return JsonResponse({"success": False, "message": "Faltan datos necesarios."}, status=400)

        try:
            # Obtener el profesional y el servicio
            profesional = Profesional.objects.get(id=profesional_id)
            servicio = Servicio.objects.get(id=servicio_id)

            # Separar fecha y hora
            fecha, hora = fecha_hora.split('T')
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            hora_obj = datetime.strptime(hora, "%H:%M").time()

            # Verificar que el horario no esté ocupado
            if Horario.objects.filter(profesional=profesional, fecha=fecha_obj, hora=hora_obj).exists():
                return JsonResponse({"success": False, "message": "El horario ya está ocupado."}, status=400)

            # Crear el turno
            Turno.objects.create(
                profesional=profesional,
                fecha_hora=fecha_hora,
                servicio=servicio,
                cliente=request.user,
            )

            # Registrar el horario como ocupado
            Horario.objects.create(
                profesional=profesional,
                fecha=fecha_obj,
                hora=hora_obj,
                disponible=False
            )

            return JsonResponse({"success": True, "message": "Turno agendado con éxito."})

        except Profesional.DoesNotExist:
            return JsonResponse({"success": False, "message": "Profesional no encontrado."})
        except Servicio.DoesNotExist:
            return JsonResponse({"success": False, "message": "Servicio no encontrado."})

    # Respuesta en caso de que el método HTTP no sea POST
    return JsonResponse({"success": False, "message": "Método no permitido."})

@login_required
def mis_turnos(request):
    """
    Obtiene los turnos activos del cliente.
    Excluye los turnos en estado 'cancelado' o 'cancelado_por_cliente'.
    """
    turnos = Turno.objects.filter(cliente=request.user).exclude(estado__in=['cancelado', 'cancelado_por_cliente']).order_by('fecha_hora')

    if not turnos.exists():
        # Retorna un mensaje indicando que no hay turnos
        return JsonResponse({"success": True, "turnos": [], "message": "No tienes turnos agendados."})

    turnos_list = []
    for turno in turnos:
        # Manejar el caso donde el formato de fecha_hora sea incorrecto
        if 'T' in turno.fecha_hora:
            fecha, hora = turno.fecha_hora.split('T')
        else:
            fecha, hora = turno.fecha_hora, "Hora no especificada"
        
        turnos_list.append({
            "id": turno.id,
            "profesional": f"{turno.profesional.usuario.first_name} {turno.profesional.usuario.last_name}",
            "fecha": fecha,
            "hora": hora,
            "servicio": turno.servicio.nombre,
            "estado": turno.estado,
        })

    return JsonResponse({"success": True, "turnos": turnos_list})


from django.contrib.auth.decorators import login_required
@login_required
def cancelar_turno(request, turno_id):
    """
    Cancela un turno del cliente y libera el horario asociado.
    """
    if request.method == "POST":
        # Obtener el turno asociado al cliente
        turno = get_object_or_404(Turno, id=turno_id, cliente=request.user)

        # Verificar si el turno ya está cancelado
        if turno.estado in ['cancelado', 'cancelado_por_cliente']:
            return JsonResponse({"success": False, "message": "El turno ya está cancelado."})

        # Validar que el turno no esté en el pasado
        if datetime.strptime(turno.fecha_hora, "%Y-%m-%dT%H:%M") < datetime.now():
            return JsonResponse({"success": False, "message": "No puedes cancelar un turno pasado."}, status=400)

        # Actualizar el estado del turno
        turno.estado = 'cancelado_por_cliente'
        turno.save()

        # Liberar el horario correspondiente
        fecha = turno.fecha_hora.split('T')[0]
        hora = turno.fecha_hora.split('T')[1]
        Horario.objects.filter(
            profesional=turno.profesional,
            fecha=fecha,
            hora=hora
        ).delete()

        return JsonResponse({"success": True, "message": "Turno cancelado con éxito."})

    return JsonResponse({"success": False, "message": "Método no permitido."})


@csrf_exempt
@login_required
def cancelar_turno_profesional(request, turno_id):
    """
    Permite al profesional cancelar un turno asignado.
    """
    if request.method == "POST":
        # Obtener el turno por su ID
        turno = get_object_or_404(Turno, id=turno_id)

        # Verificar si el turno ya está cancelado
        if turno.estado in ['cancelado', 'cancelado_por_cliente', 'cancelado_por_profesional']:
            return JsonResponse({"success": False, "message": "El turno ya está cancelado."})

        # Actualizar el estado del turno
        turno.estado = 'cancelado_por_profesional'
        turno.save()

        # Liberar el horario correspondiente
        fecha = turno.fecha_hora.split('T')[0]
        hora = turno.fecha_hora.split('T')[1]
        Horario.objects.filter(
            profesional=turno.profesional,
            fecha=fecha,
            hora=hora
        ).delete()

        return JsonResponse({"success": True, "message": "Turno cancelado con éxito."})

    return JsonResponse({"success": False, "message": "Método no permitido."})


@login_required
def profesionales_disponibles(request):
    """
    Devuelve la lista de profesionales disponibles.
    Actualmente devuelve todos los profesionales.
    """
    servicio_id = request.GET.get('servicio_id')
    profesionales = Profesional.objects.all()
    profesionales_list = [{"id": p.id, "nombre": p.usuario.get_full_name()} for p in profesionales]

    return JsonResponse({"profesionales": profesionales_list})



@login_required
def mis_turnos_profesional(request):
    """
    Devuelve los turnos asignados al profesional logueado.
    Excluye los turnos cancelados por cualquier motivo.
    """
    profesional = get_object_or_404(Profesional, usuario=request.user)
    turnos = Turno.objects.filter(profesional=profesional).exclude(
        estado__in=['cancelado', 'cancelado_por_cliente', 'cancelado_por_profesional']
    ).order_by('fecha_hora')

    turnos_list = [{
        "id": turno.id,
        "cliente": turno.cliente.get_full_name(),
        "servicio": turno.servicio.nombre,
        "fecha": turno.fecha_hora.split('T')[0],
        "hora": turno.fecha_hora.split('T')[1],
        "estado": turno.estado,
    } for turno in turnos]

    return JsonResponse({"turnos": turnos_list})