from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
from .models import Pago
from consulta.models import Turno


@login_required
def lista_pagos(request):
    """Lista de pagos del día con resumen."""
    hoy = timezone.now().date()

    # Filtros
    fecha = request.GET.get('fecha', str(hoy))
    pagos = Pago.objects.filter(fecha__date=fecha).select_related(
        'turno__paciente', 'turno__medico'
    )

    # Totales por forma de pago
    totales = pagos.values('forma_pago').annotate(
        cantidad=Count('id'),
        total=Sum('monto')
    ).order_by('forma_pago')

    total_dia = pagos.aggregate(t=Sum('monto'))['t'] or 0

    return render(request, 'facturacion/lista.html', {
        'pagos': pagos,
        'totales': totales,
        'total_dia': total_dia,
        'fecha': fecha,
        'hoy': str(hoy),
    })


@login_required
def registrar_pago(request, turno_id):
    """Registrar pago de una consulta finalizada."""
    turno = get_object_or_404(Turno, pk=turno_id)

    # Si ya tiene pago, ir directo al ticket
    if hasattr(turno, 'pago'):
        return redirect('facturacion:ticket', pago_id=turno.pago.pk)

    # Datos del médico para el concepto por defecto
    medico = turno.medico
    concepto_default = f"Consulta médica"
    if medico and medico.especialidad:
        concepto_default = f"Consulta {medico.especialidad}"

    if request.method == 'POST':
        monto = request.POST.get('monto', '0').replace(',', '.')
        try:
            monto_val = float(monto)
        except ValueError:
            monto_val = 0

        pago = Pago.objects.create(
            turno=turno,
            concepto=request.POST.get('concepto', concepto_default),
            monto=monto_val,
            forma_pago=request.POST.get('forma_pago', 'efectivo'),
            observaciones=request.POST.get('observaciones', ''),
        )
        messages.success(request, f'Pago registrado. Recibo #{pago.nro_recibo}')
        return redirect('facturacion:ticket', pago_id=pago.pk)

    return render(request, 'facturacion/registrar_pago.html', {
        'turno': turno,
        'concepto_default': concepto_default,
        'formas_pago': Pago.FORMA_PAGO,
    })


@login_required
def ticket(request, pago_id):
    """Vista del ticket imprimible (HTML → Ctrl+P)."""
    pago = get_object_or_404(Pago, pk=pago_id)

    # Marcar como impreso
    if not pago.impreso:
        pago.impreso = True
        pago.save(update_fields=['impreso'])

    # Configuración del consultorio (podés editar estos datos)
    consultorio = {
        'nombre':    'Consultorio Médico',
        'direccion': 'Dirección del consultorio',
        'telefono':  'Tel: 000-0000',
        'ciudad':    'Mendoza, Argentina',
    }

    return render(request, 'facturacion/ticket.html', {
        'pago': pago,
        'consultorio': consultorio,
    })


@login_required
def ticket_imprimir(request, pago_id):
    """Versión solo para impresión (sin sidebar, sin topbar)."""
    pago = get_object_or_404(Pago, pk=pago_id)
    consultorio = {
        'nombre':    'Consultorio Médico',
        'direccion': 'Dirección del consultorio',
        'telefono':  'Tel: 000-0000',
        'ciudad':    'Mendoza, Argentina',
    }
    return render(request, 'facturacion/ticket_print.html', {
        'pago': pago,
        'consultorio': consultorio,
    })