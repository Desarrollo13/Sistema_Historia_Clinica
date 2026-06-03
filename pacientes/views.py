from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

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
    if request.method == 'POST':
        try:
            p = Paciente.objects.create(**_paciente_data_from_post(request))
            messages.success(request, f'Paciente {p.nombre_completo} registrado correctamente.')
            return redirect('pacientes:signos_vitales', paciente_id=p.pk)
        except Exception as e:
            messages.error(request, f'Error al registrar: {e}')

    return render(request, 'pacientes/nuevo_paciente.html')


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
    })


@login_required
def signos_vitales(request, paciente_id):
    """Toma de signos vitales en recepción + envío a la cola del médico."""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    medicos = Usuario.objects.filter(rol='medico', is_active=True)

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

        # Crear turno y asignar médico automáticamente
        medico_id = request.POST.get('medico_id')
        medico = Usuario.objects.filter(pk=medico_id, rol='medico').first() if medico_id else medicos.first()

        turno = Turno.objects.create(
            paciente=paciente,
            signos=signos,
            medico=medico,
        )

        messages.success(request,
            f'Turno #{turno.numero} creado. {paciente.nombre} fue enviado al panel del Dr. {medico}.')
        return redirect('pacientes:lista')

    return render(request, 'pacientes/signos_vitales.html', {
        'paciente': paciente,
        'medicos': medicos,
    })
