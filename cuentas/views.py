from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages
from functools import wraps


# ── Decoradores de rol ─────────────────────────────────────────────────────────

def rol_requerido(*roles):
    """Decorador que restringe acceso por rol de usuario."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.es_admin or request.user.rol in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('inicio')
        return wrapper
    return decorator


def solo_medico(view_func):
    return rol_requerido('medico')(view_func)


def solo_recepcion(view_func):
    return rol_requerido('recepcion')(view_func)


# ── Vistas ─────────────────────────────────────────────────────────────────────

class LoginView(auth_views.LoginView):
    template_name = 'cuentas/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.es_medico:
            return '/consulta/panel/'
        return '/pacientes/'