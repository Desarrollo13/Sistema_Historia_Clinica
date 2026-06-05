from django.db import models, transaction
from django.utils import timezone


class ReciboCounter(models.Model):
    clave = models.CharField(max_length=20, unique=True, default='global')
    ultimo_numero = models.PositiveIntegerField(default=999)

    class Meta:
        verbose_name = 'Contador de recibos'
        verbose_name_plural = 'Contadores de recibos'

    def __str__(self):
        return f"{self.clave}: {self.ultimo_numero}"


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
            with transaction.atomic():
                counter, _ = ReciboCounter.objects.select_for_update().get_or_create(
                    clave='global',
                    defaults={'ultimo_numero': 999},
                )
                counter.ultimo_numero += 1
                counter.save(update_fields=['ultimo_numero'])
                self.nro_recibo = counter.ultimo_numero
                return super().save(*args, **kwargs)
        super().save(*args, **kwargs)
