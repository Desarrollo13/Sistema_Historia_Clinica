from django.contrib import admin
from .models import Turno, HistoriaClinica, RecetaMedicamento


class RecetaInline(admin.TabularInline):
    """Muestra los medicamentos dentro de la historia clínica."""
    model      = RecetaMedicamento
    extra      = 1
    fields     = ('medicamento', 'dosis', 'forma', 'posologia', 'cantidad')


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display  = ('numero', 'paciente', 'medico', 'estado', 'fecha_hora')
    list_filter   = ('estado', 'fecha_hora', 'medico')
    search_fields = ('paciente__apellido', 'paciente__dni')
    readonly_fields = ('numero', 'fecha_hora', 'hora_llamado',
                       'hora_inicio_atencion', 'hora_fin')
    ordering      = ('-fecha_hora',)

    fieldsets = (
        ('Turno', {
            'fields': ('numero', 'paciente', 'medico', 'estado', 'signos')
        }),
        ('Tiempos', {
            'fields': ('fecha_hora', 'hora_llamado', 'hora_inicio_atencion', 'hora_fin'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HistoriaClinica)
class HistoriaClinicaAdmin(admin.ModelAdmin):
    list_display  = ('turno', 'medico', 'diagnostico_principal', 'fecha_hora')
    list_filter   = ('fecha_hora', 'medico')
    search_fields = ('turno__paciente__apellido', 'turno__paciente__dni',
                     'diagnostico_principal')
    readonly_fields = ('fecha_hora',)
    ordering      = ('-fecha_hora',)
    inlines       = [RecetaInline]

    fieldsets = (
        ('Consulta', {
            'fields': ('turno', 'medico', 'fecha_hora')
        }),
        ('Anamnesis', {
            'fields': ('anamnesis', 'examen_fisico')
        }),
        ('Diagnóstico', {
            'fields': ('diagnostico_principal', 'diagnosticos_secundarios', 'cie10')
        }),
        ('Tratamiento', {
            'fields': ('tratamiento', 'indicaciones', 'proxima_consulta', 'derivacion')
        }),
    )


@admin.register(RecetaMedicamento)
class RecetaMedicamentoAdmin(admin.ModelAdmin):
    list_display  = ('medicamento', 'dosis', 'forma', 'posologia', 'historia')
    search_fields = ('medicamento', 'historia__turno__paciente__apellido')