from django.db import models, transaction
from django.utils import timezone


class TurnoDiarioCounter(models.Model):
    fecha = models.DateField(unique=True)
    ultimo_numero = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Contador diario de turnos'
        verbose_name_plural = 'Contadores diarios de turnos'

    def __str__(self):
        return f"{self.fecha}: {self.ultimo_numero}"


class Turno(models.Model):
    """
    Turno/cola de espera. Creado por recepción tras tomar los signos vitales.
    El médico lo ve en su panel y lo atiende.
    """
    ESTADO_CHOICES = [
        ('programado', 'Programado'),
        ('espera', 'En espera'),
        ('llamado', 'Llamado'),
        ('atencion', 'En atención'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    CANAL_CHOICES = [
        ('telefono', 'Telefono'),
        ('presencial', 'Presencial'),
        ('whatsapp', 'WhatsApp'),
    ]

    paciente = models.ForeignKey('pacientes.Paciente', on_delete=models.CASCADE,
                                  related_name='turnos')
    signos = models.OneToOneField('pacientes.SignosVitales', on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='turno')
    medico = models.ForeignKey('cuentas.Usuario', on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='turnos_asignados',
                                 limit_choices_to={'rol': 'medico'})
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='espera')
    canal_solicitud = models.CharField(max_length=15, choices=CANAL_CHOICES, default='presencial')
    motivo_turno = models.CharField(max_length=200, blank=True)
    observaciones_recepcion = models.TextField(blank=True)
    fecha_hora = models.DateTimeField(default=timezone.now)
    hora_llamado = models.DateTimeField(null=True, blank=True)
    hora_inicio_atencion = models.DateTimeField(null=True, blank=True)
    hora_fin = models.DateTimeField(null=True, blank=True)
    numero = models.PositiveIntegerField()  # número de orden del día

    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['fecha_hora']

    def __str__(self):
        return f"Turno #{self.numero} — {self.paciente} [{self.get_estado_display()}]"

    def _fecha_para_numeracion(self):
        fecha_hora = self.fecha_hora or timezone.now()
        if timezone.is_aware(fecha_hora):
            fecha_hora = timezone.localtime(fecha_hora)
        return fecha_hora.date()

    def save(self, *args, **kwargs):
        if not self.numero:
            fecha_turno = self._fecha_para_numeracion()
            with transaction.atomic():
                counter, _ = TurnoDiarioCounter.objects.select_for_update().get_or_create(
                    fecha=fecha_turno,
                    defaults={'ultimo_numero': 0},
                )
                counter.ultimo_numero += 1
                counter.save(update_fields=['ultimo_numero'])
                self.numero = counter.ultimo_numero
                return super().save(*args, **kwargs)
        super().save(*args, **kwargs)


class HistoriaClinica(models.Model):
    """Historia clínica de una consulta completa."""
    turno = models.OneToOneField(Turno, on_delete=models.CASCADE, related_name='historia')
    medico = models.ForeignKey('cuentas.Usuario', on_delete=models.SET_NULL,
                                null=True, related_name='historias_clinicas')
    fecha_hora = models.DateTimeField(default=timezone.now)

    # Anamnesis
    anamnesis = models.TextField(verbose_name='Anamnesis / Historia de la enfermedad')
    examen_fisico = models.TextField(blank=True, verbose_name='Examen físico')

    # Diagnóstico
    diagnostico_principal = models.CharField(max_length=200)
    diagnosticos_secundarios = models.TextField(blank=True)
    cie10 = models.CharField(max_length=20, blank=True, verbose_name='Código CIE-10')

    # Tratamiento
    tratamiento = models.TextField(verbose_name='Plan de tratamiento')
    indicaciones = models.TextField(blank=True, verbose_name='Indicaciones al paciente')

    # Seguimiento
    proxima_consulta = models.DateField(null=True, blank=True)
    derivacion = models.CharField(max_length=200, blank=True,
                                   verbose_name='Derivación a especialista')

    class Meta:
        verbose_name = 'Historia clínica'
        verbose_name_plural = 'Historias clínicas'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Historia de {self.turno.paciente} — {self.fecha_hora:%d/%m/%Y}"


class RecetaMedicamento(models.Model):
    """Ítem de receta (medicamento prescripto)."""
    historia = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE,
                                  related_name='receta_items')
    medicamento = models.CharField(max_length=200)
    dosis = models.CharField(max_length=100, verbose_name='Dosis / Concentración')
    forma = models.CharField(max_length=100, verbose_name='Forma farmacéutica',
                              help_text='ej: comprimidos, jarabe, inyectable')
    posologia = models.CharField(max_length=200, verbose_name='Posología',
                                  help_text='ej: 1 comprimido cada 8 horas por 7 días')
    cantidad = models.CharField(max_length=50, blank=True)
    instrucciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.medicamento} {self.dosis} — {self.posologia}"
