from django.contrib.auth import views as auth_views
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
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


@login_required
def logout_view(request):
    logout(request)
    return redirect('cuentas:login')


User = get_user_model()


def _base_user_queryset():
    return User.objects.order_by('first_name', 'last_name', 'username')


def _extract_user_data(request, *, force_role=None):
    rol = force_role or request.POST.get('rol', 'recepcion')
    return {
        'username': request.POST.get('username', '').strip(),
        'first_name': request.POST.get('first_name', '').strip(),
        'last_name': request.POST.get('last_name', '').strip(),
        'email': request.POST.get('email', '').strip(),
        'telefono': request.POST.get('telefono', '').strip(),
        'rol': rol,
        'is_active': request.POST.get('is_active') == 'on',
        'especialidad': request.POST.get('especialidad', '').strip() if rol == 'medico' else '',
        'matricula': request.POST.get('matricula', '').strip() if rol == 'medico' else '',
    }


def _save_user_from_post(request, *, user=None, force_role=None):
    data = _extract_user_data(request, force_role=force_role)
    password = request.POST.get('password', '')

    if not data['username']:
        raise ValueError('El nombre de usuario es obligatorio.')

    existing = User.objects.filter(username=data['username'])
    if user is not None:
        existing = existing.exclude(pk=user.pk)
    if existing.exists():
        raise ValueError('Ya existe un usuario con ese nombre de usuario.')

    if user is None:
        if not password:
            raise ValueError('La contraseña es obligatoria al crear un usuario.')
        user = User(**data)
        user.set_password(password)
    else:
        for field, value in data.items():
            setattr(user, field, value)
        if password:
            user.set_password(password)

    user.save()
    return user


@rol_requerido('admin')
def configuracion(request):
    usuarios = _base_user_queryset()
    return render(request, 'cuentas/configuracion.html', {
        'total_usuarios': usuarios.count(),
        'total_medicos': usuarios.filter(rol='medico', is_active=True).count(),
        'total_recepcion': usuarios.filter(rol='recepcion', is_active=True).count(),
    })


@rol_requerido('admin')
def lista_usuarios(request):
    query = request.GET.get('q', '').strip()
    usuarios = _base_user_queryset()

    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    return render(request, 'cuentas/gestion_usuarios.html', {
        'titulo': 'Usuarios del sistema',
        'usuarios': usuarios,
        'query': query,
        'crear_url': 'cuentas:nuevo_usuario',
        'editar_url': 'cuentas:editar_usuario',
        'volver_url': 'cuentas:configuracion',
    })


@rol_requerido('admin')
def lista_medicos(request):
    query = request.GET.get('q', '').strip()
    medicos = _base_user_queryset().filter(rol='medico')

    if query:
        medicos = medicos.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(especialidad__icontains=query) |
            Q(matricula__icontains=query)
        )

    return render(request, 'cuentas/gestion_usuarios.html', {
        'titulo': 'Medicos',
        'usuarios': medicos,
        'query': query,
        'crear_url': 'cuentas:nuevo_medico',
        'editar_url': 'cuentas:editar_medico',
        'volver_url': 'cuentas:configuracion',
        'solo_medicos': True,
    })


@rol_requerido('admin')
def nuevo_usuario(request):
    if request.method == 'POST':
        try:
            usuario = _save_user_from_post(request)
            messages.success(request, f'Usuario {usuario.username} creado correctamente.')
            return redirect('cuentas:lista_usuarios')
        except ValueError as exc:
            messages.error(request, str(exc))

    return render(request, 'cuentas/form_usuario.html', {
        'titulo': 'Nuevo usuario',
        'guardar_url': 'cuentas:nuevo_usuario',
        'volver_url': 'cuentas:lista_usuarios',
        'roles': User.ROL_CHOICES,
    })


@rol_requerido('admin')
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        try:
            usuario = _save_user_from_post(request, user=usuario)
            messages.success(request, f'Usuario {usuario.username} actualizado correctamente.')
            return redirect('cuentas:lista_usuarios')
        except ValueError as exc:
            messages.error(request, str(exc))

    return render(request, 'cuentas/form_usuario.html', {
        'titulo': 'Editar usuario',
        'usuario_obj': usuario,
        'guardar_url': 'cuentas:editar_usuario',
        'guardar_args': [usuario.pk],
        'volver_url': 'cuentas:lista_usuarios',
        'roles': User.ROL_CHOICES,
    })


@rol_requerido('admin')
def nuevo_medico(request):
    if request.method == 'POST':
        try:
            medico = _save_user_from_post(request, force_role='medico')
            messages.success(request, f'Medico {medico.get_full_name() or medico.username} creado correctamente.')
            return redirect('cuentas:lista_medicos')
        except ValueError as exc:
            messages.error(request, str(exc))

    return render(request, 'cuentas/form_usuario.html', {
        'titulo': 'Nuevo medico',
        'guardar_url': 'cuentas:nuevo_medico',
        'volver_url': 'cuentas:lista_medicos',
        'solo_medicos': True,
    })


@rol_requerido('admin')
def editar_medico(request, user_id):
    medico = get_object_or_404(User, pk=user_id, rol='medico')

    if request.method == 'POST':
        try:
            medico = _save_user_from_post(request, user=medico, force_role='medico')
            messages.success(request, f'Medico {medico.get_full_name() or medico.username} actualizado correctamente.')
            return redirect('cuentas:lista_medicos')
        except ValueError as exc:
            messages.error(request, str(exc))

    return render(request, 'cuentas/form_usuario.html', {
        'titulo': 'Editar medico',
        'usuario_obj': medico,
        'guardar_url': 'cuentas:editar_medico',
        'guardar_args': [medico.pk],
        'volver_url': 'cuentas:lista_medicos',
        'solo_medicos': True,
    })
