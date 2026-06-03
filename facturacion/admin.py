from django.contrib import admin
from .models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display  = ('nro_recibo', 'turno', 'concepto', 'forma_pago', 'monto', 'fecha', 'impreso')
    list_filter   = ('forma_pago', 'impreso', 'fecha')
    search_fields = ('turno__paciente__apellido', 'turno__paciente__dni',
                     'concepto', 'nro_recibo')
    readonly_fields = ('nro_recibo', 'fecha')
    ordering      = ('-fecha',)

    fieldsets = (
        ('Comprobante', {
            'fields': ('nro_recibo', 'turno', 'fecha')
        }),
        ('Pago', {
            'fields': ('concepto', 'monto', 'forma_pago', 'observaciones', 'impreso')
        }),
    )