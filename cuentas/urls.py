from django.urls import path
from .views import (
    LoginView,
    configuracion,
    editar_medico,
    editar_usuario,
    lista_medicos,
    lista_usuarios,
    logout_view,
    nuevo_medico,
    nuevo_usuario,
)

app_name = 'cuentas'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('configuracion/', configuracion, name='configuracion'),
    path('configuracion/usuarios/', lista_usuarios, name='lista_usuarios'),
    path('configuracion/usuarios/nuevo/', nuevo_usuario, name='nuevo_usuario'),
    path('configuracion/usuarios/<int:user_id>/editar/', editar_usuario, name='editar_usuario'),
    path('configuracion/medicos/', lista_medicos, name='lista_medicos'),
    path('configuracion/medicos/nuevo/', nuevo_medico, name='nuevo_medico'),
    path('configuracion/medicos/<int:user_id>/editar/', editar_medico, name='editar_medico'),
]
