from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import Paciente, SignosVitales
from consulta.models import Turno
from cuentas.models import Usuario


PACIENTE_FIELDS = (
    'dni', 'apellido', 'nombre', 'fecha_nacimiento', 'sexo',
    'telefono', 'email', 'domicilio', 'ciudad',
    'grupo_sanguineo', 'obra_social', 'nro_afiliado',
    'alergias', 'antecedentes', 'medicacion_habitual',
)


def _paciente_data_from_post(request):
    return {
        'dni': request.POST['dni'],
        'apellido': request.POST['apellido'],
        'nombre': request.POST['nombre'],
        'fecha_nacimiento': request.POST['fecha_nacimiento'],
        'sexo': request.POST['sexo'],
        'telefono': request.POST.get('telefono', ''),
        'email': request.POST.get('email', ''),
        'domicilio': request.POST.get('domicilio', ''),
        'ciudad': request.POST.get('ciudad', ''),
        'grupo_sanguineo': request.POST.get('grupo_sanguineo', ''),
        'obra_social': request.POST.get('obra_social', ''),
        'nro_afiliado': request.POST.get('nro_afiliado', ''),
        'alergias': request.POST.get('alergias', ''),
        'antecedentes': request.POST.get('antecedentes', ''),
        'medicacion_habitual': request.POST.get('medicacion_habitual', ''),
    }


def _medicos_activos():
    return Usuario.objects.filter(rol='medico', is_active=True).order_by('first_name', 'last_name', 'username')


def _turnos_programados_del_paciente(paciente):
    return paciente.turnos.filter(
        estado='programado',
        fecha_hora__gte=timezone.now(),
    ).select_related('medico').order_by('fecha_hora')


def _parse_fecha_hora_turno(value):
    fecha_hora = parse_datetime(value)
    if fecha_hora is None:
        raise ValueError('Debes indicar una fecha y hora validas.')
    if timezone.is_naive(fecha_hora):
        fecha_hora = timezone.make_aware(fecha_hora, timezone.get_current_timezone())
    if fecha_hora <= timezone.now():
        raise ValueError('La fecha y hora del turno debe ser futura.')
    return fecha_hora


def _buscar_turno_programado_hoy(paciente, turno_id=None):
    turnos = paciente.turnos.filter(estado='programado', fecha_hora__date=timezone.localdate()).order_by('fecha_hora')
    if turno_id:
        turnos = turnos.filter(pk=turno_id)
    return turnos.first()


@login_required
def lista_pacientes(request):
    query = request.GET.get('q', '').strip()
    pacientes = Paciente.objects.filter(activo=True)

    if query:
        pacientes = pacientes.filter(
            Q(dni__icontains=query) |
            Q(apellido__icontains=query) |
            Q(nombre__icontains=query)
        )

    return render(request, 'pacientes/lista.html', {
        'pacientes': pacientes[:50],
        'query': query,
        'mostrar_inactivos': False,
        'modo_agenda': request.GET.get('modo') == 'agenda',
    })


@login_required
def lista_pacientes_inactivos(request):
    query = request.GET.get('q', '').strip()
    pacientes = Paciente.objects.filter(activo=False)

    if query:
        pacientes = pacientes.filter(
            Q(dni__icontains=query) |
            Q(apellido__icontains=query) |
            Q(nombre__icontains=query)
        )

    return render(request, 'pacientes/lista.html', {
        'pacientes': pacientes[:50],
        'query': query,
        'mostrar_inactivos': True,
    })


@login_required
def buscar_paciente_ajax(request):
    """Búsqueda rápida para autocompletar."""
    q = request.GET.get('q', '')
    resultados = Paciente.objects.filter(
        Q(dni__icontains=q) | Q(apellido__icontains=q) | Q(nombre__icontains=q),
        activo=True
    )[:10]
    data = [{'id': p.pk, 'text': str(p), 'dni': p.dni} for p in resultados]
    return JsonResponse({'resultados': data})


@login_required
def nuevo_paciente(request):
    next_step = request.GET.get('next', '')

    if request.method == 'POST':
        try:
            p = Paciente.objects.create(**_paciente_data_from_post(request))
            messages.success(request, f'Paciente {p.nombre_completo} registrado correctamente.')
            if next_step == 'agendar':
                return redirect('pacientes:agendar_turno', paciente_id=p.pk)
            return redirect('pacientes:signos_vitales', paciente_id=p.pk)
        except Exception as e:
            messages.error(request, f'Error al registrar: {e}')

    return render(request, 'pacientes/nuevo_paciente.html', {'next_step': next_step})


@login_required
def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk, activo=True)

    if request.method == 'POST':
        try:
            for field, value in _paciente_data_from_post(request).items():
                setattr(paciente, field, value)
            paciente.save(update_fields=PACIENTE_FIELDS + ('actualizado',))
            messages.success(request, f'Paciente {paciente.nombre_completo} actualizado correctamente.')
            return redirect('pacientes:detalle', pk=paciente.pk)
        except Exception as e:
            messages.error(request, f'Error al actualizar: {e}')

    return render(request, 'pacientes/editar_paciente.html', {'paciente': paciente})


@login_required
def desactivar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk, activo=True)

    if request.method != 'POST':
        return redirect('pacientes:detalle', pk=paciente.pk)

    paciente.activo = False
    paciente.save(update_fields=['activo', 'actualizado'])
    messages.success(request, f'Paciente {paciente.nombre_completo} dado de baja correctamente.')
    return redirect('pacientes:lista')


@login_required
def reactivar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk, activo=False)

    if request.method != 'POST':
        return redirect('pacientes:inactivos')

    paciente.activo = True
    paciente.save(update_fields=['activo', 'actualizado'])
    messages.success(request, f'Paciente {paciente.nombre_completo} reactivado correctamente.')
    return redirect('pacientes:inactivos')


@login_required
def detalle_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    historial = paciente.turnos.filter(estado='finalizado').select_related('historia').order_by('-fecha_hora')
    return render(request, 'pacientes/detalle.html', {
        'paciente': paciente,
        'historial': historial,
        'turnos_programados': _turnos_programados_del_paciente(paciente)[:5],
    })


@login_required
def agendar_turno(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id, activo=True)
    medicos = _medicos_activos()
    turnos_programados = _turnos_programados_del_paciente(paciente)[:5]

    if request.method == 'POST':
        try:
            fecha_hora = _parse_fecha_hora_turno(request.POST.get('fecha_hora', ''))
            medico = get_object_or_404(Usuario, pk=request.POST.get('medico_id'), rol='medico', is_active=True)

            if Turno.objects.filter(
                medico=medico,
                fecha_hora=fecha_hora,
            ).exclude(estado='cancelado').exists():
                raise ValueError('Ese medico ya tiene un turno asignado en esa fecha y hora.')

            if Turno.objects.filter(
                paciente=paciente,
                fecha_hora=fecha_hora,
            ).exclude(estado='cancelado').exists():
                raise ValueError('El paciente ya tiene un turno cargado en esa fecha y hora.')

            turno = Turno.objects.create(
                paciente=paciente,
                medico=medico,
                estado='programado',
                canal_solicitud=request.POST.get('canal_solicitud', 'presencial'),
                motivo_turno=request.POST.get('motivo_turno', '').strip(),
                observaciones_recepcion=request.POST.get('observaciones_recepcion', '').strip(),
                fecha_hora=fecha_hora,
            )
            messages.success(
                request,
                f'Turno #{turno.numero} agendado para el {timezone.localtime(turno.fecha_hora):%d/%m/%Y %H:%M}.',
            )
            return redirect('pacientes:detalle', pk=paciente.pk)
        except Exception as e:
            messages.error(request, f'No se pudo agendar el turno: {e}')

    return render(request, 'pacientes/agendar_turno.html', {
        'paciente': paciente,
        'medicos': medicos,
        'turnos_programados': turnos_programados,
        'canales': Turno.CANAL_CHOICES,
        'fecha_minima': timezone.localtime().strftime('%Y-%m-%dT%H:%M'),
    })


@login_required
def signos_vitales(request, paciente_id):
    """Toma de signos vitales en recepción + envío a la cola del médico."""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    medicos = _medicos_activos()
    turno_programado = _buscar_turno_programado_hoy(paciente, request.GET.get('turno_id'))

    if request.method == 'POST':
        signos = SignosVitales.objects.create(
            paciente=paciente,
            tomados_por=request.user,
            presion_sistolica=request.POST.get('presion_sistolica') or None,
            presion_diastolica=request.POST.get('presion_diastolica') or None,
            frecuencia_cardiaca=request.POST.get('frecuencia_cardiaca') or None,
            frecuencia_respiratoria=request.POST.get('frecuencia_respiratoria') or None,
            temperatura=request.POST.get('temperatura') or None,
            saturacion_o2=request.POST.get('saturacion_o2') or None,
            peso=request.POST.get('peso') or None,
            talla=request.POST.get('talla') or None,
            motivo_consulta=request.POST.get('motivo_consulta', ''),
            observaciones=request.POST.get('observaciones', ''),
        )

        medico_id = request.POST.get('medico_id')
        medico = Usuario.objects.filter(pk=medico_id, rol='medico').first() if medico_id else (turno_programado.medico if turno_programado else medicos.first())

        if turno_programado:
            turno_programado.signos = signos
            turno_programado.medico = medico
            turno_programado.estado = 'espera'
            turno_programado.motivo_turno = request.POST.get('motivo_consulta', '').strip() or turno_programado.motivo_turno
            turno_programado.observaciones_recepcion = request.POST.get('observaciones', '').strip() or turno_programado.observaciones_recepcion
            turno_programado.save(update_fields=['signos', 'medico', 'estado', 'motivo_turno', 'observaciones_recepcion'])
            turno = turno_programado
            messages.success(
                request,
                f'Turno programado #{turno.numero} confirmado. {paciente.nombre} fue enviado al panel del Dr. {medico}.',
            )
        else:
            turno = Turno.objects.create(
                paciente=paciente,
                signos=signos,
                medico=medico,
                canal_solicitud='presencial',
                motivo_turno=request.POST.get('motivo_consulta', '').strip(),
                observaciones_recepcion=request.POST.get('observaciones', '').strip(),
            )
            messages.success(
                request,
                f'Turno #{turno.numero} creado. {paciente.nombre} fue enviado al panel del Dr. {medico}.',
            )
        return redirect('pacientes:lista')

    return render(request, 'pacientes/signos_vitales.html', {
        'paciente': paciente,
        'medicos': medicos,
        'turno_programado': turno_programado,
    })
