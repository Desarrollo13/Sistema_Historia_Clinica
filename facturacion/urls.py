from django.urls import path
from . import views

app_name = 'facturacion'

urlpatterns = [
    path('',                          views.lista_pagos,      name='lista'),
    path('pago/<int:turno_id>/',      views.registrar_pago,   name='registrar'),
    path('ticket/<int:pago_id>/',     views.ticket,           name='ticket'),
    path('ticket/<int:pago_id>/print/',views.ticket_imprimir, name='ticket_print'),
]