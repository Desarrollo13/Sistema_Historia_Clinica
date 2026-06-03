from django.db import models
from django.utils import timezone


class Pago(models.Model):
    FORMA_PAGO = [
        ('efectivo',      'Efectivo'),
        ('tarjeta_deb',   'Tarjeta débito'),
        ('tarjeta_cred',  'Tarjeta crédito'),
        ('transferencia', 'Transferencia'),
        ('obra_social',   'Obra social'),
        ('sin_cargo',     'Sin cargo'),
    ]

    turno      = models.OneToOneField('consulta.Turno', on_delete=models.CASCADE,
                                       related_name='pago')
    concepto   = models.CharField(max_length=200, default='Consulta médica')
    monto      = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO, default='efectivo')
    fecha      = models.DateTimeField(default=timezone.now)
    impreso    = models.BooleanField(default=False)
    nro_recibo = models.PositiveIntegerField(unique=True, editable=False)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha']

    def __str__(self):
        return f"Recibo #{self.nro_recibo} — {self.turno.paciente} — ${self.monto}"

    def save(self, *args, **kwargs):
        if not self.nro_recibo:
            ultimo = Pago.objects.order_by('nro_recibo').last()
            self.nro_recibo = (ultimo.nro_recibo + 1) if ultimo else 1000
        super().save(*args, **kwargs)