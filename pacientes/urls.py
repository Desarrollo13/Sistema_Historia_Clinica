# pacientes/urls.py
from django.urls import path
from . import views

app_name = 'pacientes'

urlpatterns = [
    path('',              views.lista_pacientes,      name='lista'),
    path('inactivos/',    views.lista_pacientes_inactivos, name='inactivos'),
    path('nuevo/',        views.nuevo_paciente,       name='nuevo'),
    path('buscar/',       views.buscar_paciente_ajax, name='buscar_ajax'),
    path('<int:pk>/editar/', views.editar_paciente,   name='editar'),
    path('<int:pk>/baja/',   views.desactivar_paciente, name='baja'),
    path('<int:pk>/reactivar/', views.reactivar_paciente, name='reactivar'),
    path('<int:pk>/',     views.detalle_paciente,     name='detalle'),
    path('<int:paciente_id>/signos/', views.signos_vitales, name='signos_vitales'),
]
