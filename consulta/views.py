from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.views.decorators.http import require_POST

from pacientes.models import Paciente, SignosVitales
from .models import Turno, HistoriaClinica, RecetaMedicamento
from cuentas.views import solo_medico, rol_requerido


# ── Panel del médico ────────────────────────────────────────────────────────────

@solo_medico
def panel_medico(request):
    """Vista principal del médico: lista de pacientes en espera."""
    hoy = timezone.now().date()
    turnos_espera = Turno.objects.filter(
        fecha_hora__date=hoy,
        estado__in=['espera', 'llamado'],
        medico=request.user
    ).select_related('paciente', 'signos').order_by('fecha_hora')

    turnos_atendidos = Turno.objects.filter(
        fecha_hora__date=hoy,
        estado='finalizado',
        medico=request.user
    ).count()

    return render(request, 'consulta/panel_medico.html', {
        'turnos': turnos_espera,
        'atendidos_hoy': turnos_atendidos,
    })


@solo_medico
def llamar_paciente(request, turno_id):
    turno = get_object_or_404(Turno, pk=turno_id, medico=request.user)
    turno.estado = 'llamado'
    turno.hora_llamado = timezone.now()
    turno.save()
    messages.success(request, f'Paciente {turno.paciente.nombre_completo} llamado.')
    return redirect('consulta:panel_medico')


@solo_medico
def iniciar_consulta(request, turno_id):
    turno = get_object_or_404(Turno, pk=turno_id, medico=request.user)
    turno.estado = 'atencion'
    turno.hora_inicio_atencion = timezone.now()
    turno.save()
    return redirect('consulta:nueva_historia', turno_id=turno.pk)


@solo_medico
def nueva_historia(request, turno_id):
    turno = get_object_or_404(Turno, pk=turno_id, medico=request.user)
    paciente = turno.paciente
    historial = HistoriaClinica.objects.filter(
        turno__paciente=paciente
    ).order_by('-fecha_hora')[:5]

    if request.method == 'POST':
        historia = HistoriaClinica.objects.create(
            turno=turno,
            medico=request.user,
            anamnesis=request.POST.get('anamnesis', ''),
            examen_fisico=request.POST.get('examen_fisico', ''),
            diagnostico_principal=request.POST.get('diagnostico_principal', ''),
            diagnosticos_secundarios=request.POST.get('diagnosticos_secundarios', ''),
            cie10=request.POST.get('cie10', ''),
            tratamiento=request.POST.get('tratamiento', ''),
            indicaciones=request.POST.get('indicaciones', ''),
            proxima_consulta=request.POST.get('proxima_consulta') or None,
            derivacion=request.POST.get('derivacion', ''),
        )

        # Guardar medicamentos de la receta
        medicamentos = request.POST.getlist('medicamento[]')
        dosis_list = request.POST.getlist('dosis[]')
        forma_list = request.POST.getlist('forma[]')
        posologia_list = request.POST.getlist('posologia[]')

        for i, med in enumerate(medicamentos):
            if med.strip():
                RecetaMedicamento.objects.create(
                    historia=historia,
                    medicamento=med,
                    dosis=dosis_list[i] if i < len(dosis_list) else '',
                    forma=forma_list[i] if i < len(forma_list) else '',
                    posologia=posologia_list[i] if i < len(posologia_list) else '',
                )

        turno.estado = 'finalizado'
        turno.hora_fin = timezone.now()
        turno.save()

        messages.success(request, 'Historia clínica guardada correctamente.')
        return redirect('consulta:panel_medico')

    return render(request, 'consulta/nueva_historia.html', {
        'turno': turno,
        'paciente': paciente,
        'signos': turno.signos,
        'historial': historial,
    })


@login_required
def ver_historia(request, historia_id):
    historia = get_object_or_404(HistoriaClinica, pk=historia_id)
    return render(request, 'consulta/ver_historia.html', {'historia': historia})


# ── API para polling (actualización automática del panel médico) ───────────────

@solo_medico
def api_turnos_espera(request):
    """Endpoint JSON para actualización en tiempo real del panel."""
    hoy = timezone.now().date()
    turnos = Turno.objects.filter(
        fecha_hora__date=hoy,
        estado__in=['espera', 'llamado'],
        medico=request.user
    ).select_related('paciente', 'signos').order_by('fecha_hora')

    data = [{
        'id': t.pk,
        'numero': t.numero,
        'paciente': t.paciente.nombre_completo,
        'motivo': t.signos.motivo_consulta if t.signos else '—',
        'hora': t.fecha_hora.strftime('%H:%M'),
        'estado': t.estado,
        'presion': t.signos.presion if t.signos else '—',
        'temperatura': str(t.signos.temperatura) if t.signos and t.signos.temperatura else '—',
        'saturacion': str(t.signos.saturacion_o2) if t.signos and t.signos.saturacion_o2 else '—',
    } for t in turnos]

    return JsonResponse({'turnos': data})