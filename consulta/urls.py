# consulta/urls.py
from django.urls import path
from . import views

app_name = 'consulta'

urlpatterns = [
    path('panel/',                         views.panel_medico,      name='panel_medico'),
    path('llamar/<int:turno_id>/',         views.llamar_paciente,   name='llamar'),
    path('iniciar/<int:turno_id>/',        views.iniciar_consulta,  name='iniciar'),
    path('historia/<int:turno_id>/nueva/', views.nueva_historia,    name='nueva_historia'),
    path('historia/<int:historia_id>/',    views.ver_historia,      name='ver_historia'),
    path('historia/<int:historia_id>/receta.pdf', views.receta_pdf, name='receta_pdf'),
    path('api/turnos/',                    views.api_turnos_espera, name='api_turnos'),
]
