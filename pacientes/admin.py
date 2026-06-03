from django.contrib import admin
from .models import Paciente, SignosVitales


class SignosVitalesInline(admin.TabularInline):
    """Muestra los signos vitales dentro de la ficha del paciente."""
    model   = SignosVitales
    extra   = 0
    readonly_fields = ('fecha_hora', 'tomados_por', 'presion_sistolica',
                       'presion_diastolica', 'frecuencia_cardiaca', 'temperatura',
                       'saturacion_o2', 'peso', 'talla', 'motivo_consulta')
    can_delete = False
    show_change_link = True


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display   = ('dni', 'apellido', 'nombre', 'edad', 'obra_social', 'telefono', 'activo')
    list_filter    = ('activo', 'sexo', 'obra_social')
    search_fields  = ('dni', 'apellido', 'nombre', 'telefono')
    ordering       = ('apellido', 'nombre')
    inlines        = [SignosVitalesInline]

    fieldsets = (
        ('Identificación', {
            'fields': ('dni', 'apellido', 'nombre', 'fecha_nacimiento', 'sexo', 'grupo_sanguineo')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'domicilio', 'ciudad')
        }),
        ('Antecedentes médicos', {
            'fields': ('alergias', 'antecedentes', 'medicacion_habitual'),
            'classes': ('collapse',)
        }),
        ('Cobertura médica', {
            'fields': ('obra_social', 'nro_afiliado'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


@admin.register(SignosVitales)
class SignosVitalesAdmin(admin.ModelAdmin):
    list_display  = ('paciente', 'fecha_hora', 'tomados_por', 'presion',
                     'temperatura', 'saturacion_o2', 'motivo_consulta')
    list_filter   = ('fecha_hora', 'tomados_por')
    search_fields = ('paciente__apellido', 'paciente__dni', 'motivo_consulta')
    readonly_fields = ('fecha_hora',)
    ordering      = ('-fecha_hora',)