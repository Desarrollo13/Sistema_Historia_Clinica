from django.db import models
from django.utils import timezone


class Paciente(models.Model):
    SEXO_CHOICES = [('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')]
    SANGRE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]

    # Identificación
    dni = models.CharField(max_length=20, unique=True, verbose_name='DNI / Cédula')
    apellido = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    grupo_sanguineo = models.CharField(max_length=3, choices=SANGRE_CHOICES, blank=True)

    # Contacto
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    domicilio = models.CharField(max_length=200, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)

    # Antecedentes médicos
    alergias = models.TextField(blank=True)
    antecedentes = models.TextField(blank=True)
    medicacion_habitual = models.TextField(blank=True)

    # Seguro médico
    obra_social = models.CharField(max_length=100, blank=True)
    nro_afiliado = models.CharField(max_length=50, blank=True)

    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (DNI: {self.dni})"

    @property
    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"

    @property
    def edad(self):
        today = timezone.now().date()
        born = self.fecha_nacimiento
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class SignosVitales(models.Model):
    """Registro de signos vitales tomados en recepción."""
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE,
                                  related_name='signos_vitales')
    tomados_por = models.ForeignKey('cuentas.Usuario', on_delete=models.SET_NULL,
                                     null=True, related_name='signos_tomados')
    fecha_hora = models.DateTimeField(default=timezone.now)

    # Signos vitales
    presion_sistolica = models.PositiveSmallIntegerField(null=True, blank=True,
                                                          verbose_name='Presión sistólica (mmHg)')
    presion_diastolica = models.PositiveSmallIntegerField(null=True, blank=True,
                                                           verbose_name='Presión diastólica (mmHg)')
    frecuencia_cardiaca = models.PositiveSmallIntegerField(null=True, blank=True,
                                                            verbose_name='FC (lpm)')
    frecuencia_respiratoria = models.PositiveSmallIntegerField(null=True, blank=True,
                                                                verbose_name='FR (rpm)')
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True,
                                       verbose_name='Temperatura (°C)')
    saturacion_o2 = models.PositiveSmallIntegerField(null=True, blank=True,
                                                      verbose_name='SatO₂ (%)')
    peso = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True,
                                verbose_name='Peso (kg)')
    talla = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True,
                                 verbose_name='Talla (cm)')
    motivo_consulta = models.TextField(verbose_name='Motivo de consulta')
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Signos vitales'
        verbose_name_plural = 'Signos vitales'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Signos de {self.paciente} — {self.fecha_hora:%d/%m/%Y %H:%M}"

    @property
    def imc(self):
        if self.peso and self.talla and self.talla > 0:
            talla_m = float(self.talla) / 100
            return round(float(self.peso) / (talla_m ** 2), 1)
        return None

    @property
    def presion(self):
        if self.presion_sistolica and self.presion_diastolica:
            return f"{self.presion_sistolica}/{self.presion_diastolica}"
        return '—'