# Sistema de Historia Clinica

Sistema web para consultorio medico orientado a recepcion, atencion medica y facturacion en red local.

Permite trabajar desde varias computadoras sobre una misma base de datos y seguir el flujo completo del paciente: alta, agenda, recepcion, consulta, receta y cobro.

## Que hace el software

- Registro, busqueda y edicion de pacientes.
- Baja logica y reactivacion de pacientes sin perder historial.
- Agenda de turnos por `telefono`, `presencial` o `WhatsApp`.
- Validacion de disponibilidad por medico, fecha y hora.
- Recepcion con toma de signos vitales.
- Reutilizacion del turno programado cuando el paciente llega.
- Panel medico con cola de espera.
- Carga de historia clinica.
- Generacion de receta en PDF.
- Registro de pagos y emision de ticket.
- Gestion simple de usuarios y medicos desde una pantalla propia de configuracion.

## Flujo principal

1. Recepcion busca o registra al paciente.
2. Si el turno se pide por telefono, presencial o WhatsApp, recepcion lo agenda.
3. Cuando el paciente llega, recepcion toma signos vitales.
4. El sistema confirma el turno del dia y lo envia al panel del medico.
5. El medico llama al paciente, inicia la consulta y guarda la historia clinica.
6. Se puede abrir la receta en PDF.
7. Recepcion o administracion registra el pago.
8. El sistema genera el ticket de cobro.

## Modulos principales

- `cuentas`: login, logout, roles y configuracion operativa.
- `pacientes`: padron de pacientes, agenda y recepcion.
- `consulta`: cola del medico, turnos, historia clinica y receta PDF.
- `facturacion`: pagos y tickets.

## Roles del sistema

### Recepcion

- Registra y edita pacientes.
- Agenda turnos.
- Toma signos vitales.
- Registra pagos.
- Imprime tickets.

### Medico

- Ve solo su cola de espera.
- Llama pacientes.
- Inicia consulta.
- Guarda historia clinica.
- Abre receta PDF.

### Administrador

- Tiene acceso general.
- Usa `Configuracion` para gestionar usuarios y medicos sin entrar al admin tecnico.
- Puede operar facturacion.

## Funciones destacadas

### Pacientes

- Pacientes activos en `/pacientes/`.
- Pacientes inactivos en `/pacientes/inactivos/`.
- Baja logica con `activo=False`.
- Historial conservado aunque el paciente se desactive.

### Agenda de turnos

- Desde la lista o ficha del paciente se puede usar `Agendar turno`.
- Si el paciente no existe, primero se crea y luego se agenda.
- El turno programado guarda:
  - medico
  - fecha y hora
  - canal de solicitud
  - motivo
  - observaciones de recepcion
- El sistema evita:
  - dos turnos para el mismo medico en el mismo horario
  - dos turnos del mismo paciente en el mismo horario

### Recepcion y signos vitales

- Al tomar signos se crea `SignosVitales`.
- Si ya habia un turno `programado` para ese dia, el sistema lo reutiliza y lo pasa a `espera`.
- Si no habia turno previo, se crea uno nuevo en ese momento.

### Consulta medica

- El medico trabaja sobre su panel en `/consulta/panel/`.
- Puede llamar al paciente e iniciar la atencion.
- Al guardar la historia clinica:
  - se crea `HistoriaClinica`
  - se guardan los medicamentos de receta
  - el turno pasa a `finalizado`

### Receta PDF

- Se genera desde una historia clinica ya guardada.
- Usa datos del consultorio configurados por entorno.

### Facturacion

- Solo `recepcion` y `admin` pueden facturar.
- Solo se cobra un turno `finalizado`.
- `Pago` esta vinculado `OneToOne` con `Turno`.
- Si un turno ya fue cobrado, se redirige al ticket existente.

### Configuracion operativa

- Disponible solo para administradores.
- Reemplaza el uso normal del admin tecnico de Django.
- Incluye:
  - `Gestionar usuarios`
  - `Gestionar medicos`

## Tecnologias

- Python
- Django
- SQLite
- ReportLab
- Pillow
- `django-widget-tweaks`

## Requisitos

- Windows con `venv\Scripts\python.exe` disponible en este checkout.
- Python compatible con Django 4.2 o superior.

Dependencias declaradas en `requirements.txt`:

```txt
Django>=4.2
Pillow>=10.0
reportlab>=4.0
python-escpos>=3.0
django-widget-tweaks>=1.5
```

## Instalacion

```powershell
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe manage.py migrate
```

## Ejecucion

Servidor local:

```powershell
venv\Scripts\python.exe manage.py runserver
```

Servidor LAN:

```powershell
iniciar_servidor_lan.bat
```

El script LAN:

1. carga variables de entorno
2. ejecuta `collectstatic`
3. aplica migraciones
4. inicia el servidor en `0.0.0.0:8000`

## Variables de entorno

Configuracion principal leida desde `clinica/settings.py`:

- `CLINICA_SECRET_KEY`
- `CLINICA_DEBUG`
- `CLINICA_ALLOWED_HOSTS`
- `CLINICA_CONSULTORIO_NOMBRE`
- `CLINICA_CONSULTORIO_DIRECCION`
- `CLINICA_CONSULTORIO_TELEFONO`
- `CLINICA_CONSULTORIO_EMAIL`
- `CLINICA_CONSULTORIO_CIUDAD`
- `CLINICA_CONSULTORIO_LOGO`

Detalles actuales:

- `DEBUG` queda apagado por defecto si no se define `CLINICA_DEBUG`.
- `ALLOWED_HOSTS` no usa `*` por defecto.
- La identidad del consultorio alimenta tickets y recetas.

## Base de datos y archivos

- Base de datos: `db.sqlite3`
- Media: `media/`
- Estaticos recolectados: `staticfiles/`
- Templates centralizados: `templates/`

## Comandos utiles

Verificacion rapida:

```powershell
venv\Scripts\python.exe manage.py check
```

Tests principales:

```powershell
venv\Scripts\python.exe manage.py test cuentas pacientes consulta facturacion
```

Tests por app:

```powershell
venv\Scripts\python.exe manage.py test pacientes
venv\Scripts\python.exe manage.py test consulta
venv\Scripts\python.exe manage.py test facturacion
venv\Scripts\python.exe manage.py test cuentas
```

## Documentacion adicional

- Manual funcional: `docs/manual_sistema.md`
- Manual en PDF: `docs/manual_sistema.pdf`

## Notas importantes del repo

- No usar `python setup.py` como flujo normal. En este repo es un script de bootstrap que instala dependencias, reescribe `requirements.txt`, corre migraciones y crea `admin/admin123`.
- El usuario del sistema es `cuentas.Usuario`, no el `User` por defecto de Django.
- La raiz `/` redirige a `/pacientes/`.
- El flujo operativo principal es `pacientes -> consulta -> facturacion`.

## Estado actual

El sistema ya cubre:

- recepcion
- agenda de turnos
- consulta medica
- receta PDF
- facturacion
- tickets
- roles de acceso
- configuracion operativa simple
- pruebas automaticas sobre flujos criticos
