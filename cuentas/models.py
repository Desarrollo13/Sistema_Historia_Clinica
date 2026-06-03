from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('medico', 'Médico'),
        ('recepcion', 'Recepción'),
    ]

    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='recepcion')
    telefono = models.CharField(max_length=20, blank=True)
    especialidad = models.CharField(max_length=100, blank=True,
                                    help_text="Solo para médicos")
    matricula = models.CharField(max_length=50, blank=True,
                                 help_text="Matrícula profesional del médico")

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"

    @property
    def es_admin(self):
        return self.rol == 'admin' or self.is_superuser

    @property
    def es_medico(self):
        return self.rol == 'medico'

    @property
    def es_recepcion(self):
        return self.rol == 'recepcion'