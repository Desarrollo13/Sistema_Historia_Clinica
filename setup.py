"""
Script de instalación automática del Sistema de Historias Clínicas.
Ejecutar una sola vez: python setup.py
"""
import os
import subprocess
import sys

REQUIREMENTS = """
Django>=4.2
Pillow>=10.0
reportlab>=4.0
python-escpos>=3.0
django-widget-tweaks>=1.5
""".strip()

STRUCTURE = [
    "clinica",
    "pacientes",
    "consulta",
    "facturacion",
    "cuentas",
    "static/css",
    "static/js",
    "media/recetas",
    "templates/base",
    "templates/pacientes",
    "templates/consulta",
    "templates/facturacion",
    "templates/cuentas",
]

def main():
    print("=" * 50)
    print("  Sistema de Historias Clínicas - Setup")
    print("=" * 50)

    # Crear estructura de directorios
    for path in STRUCTURE:
        os.makedirs(path, exist_ok=True)
        print(f"  ✓ {path}/")

    # Escribir requirements.txt
    with open("requirements.txt", "w") as f:
        f.write(REQUIREMENTS)
    print("\n  ✓ requirements.txt creado")

    # Instalar dependencias
    print("\n  Instalando dependencias...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
    print("  ✓ Dependencias instaladas")

    # Migraciones
    print("\n  Aplicando migraciones...")
    subprocess.check_call([sys.executable, "manage.py", "migrate"])

    # Crear superusuario por defecto
    print("\n  Creando usuario administrador (admin / admin123)...")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clinica.settings")
    import django
    django.setup()
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@clinica.local", "admin123")
        print("  ✓ Superusuario creado")

    print("\n" + "=" * 50)
    print("  ¡Instalación completada!")
    print("  Ejecuta: python manage.py runserver 0.0.0.0:8000")
    print("  Accede desde cualquier PC: http://[IP-SERVIDOR]:8000")
    print("=" * 50)

if __name__ == "__main__":
    main()