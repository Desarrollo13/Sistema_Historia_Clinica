from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ('username', 'get_full_name', 'rol', 'especialidad', 'matricula', 'is_active')
    list_filter   = ('rol', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering      = ('last_name', 'first_name')

    # Campos que se muestran al EDITAR un usuario existente
    fieldsets = UserAdmin.fieldsets + (
        ('Datos del consultorio', {
            'fields': ('rol', 'telefono', 'especialidad', 'matricula')
        }),
    )

    # Campos que se muestran al CREAR un usuario nuevo
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos del consultorio', {
            'fields': ('first_name', 'last_name', 'email',
                       'rol', 'telefono', 'especialidad', 'matricula')
        }),
    )