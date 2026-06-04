# Manual del Sistema de Historia Clinica

## 1. Objetivo

Este sistema permite trabajar la atencion de un consultorio medico en red local desde varias computadoras.

Flujo principal:

1. Recepcion registra o busca al paciente.
2. Si el turno se solicita por telefono, presencial o WhatsApp, recepcion agenda fecha, hora y medico.
3. Cuando el paciente llega, recepcion toma signos vitales.
4. El sistema confirma el turno del dia y lo envia al medico.
5. El medico atiende al paciente y completa la historia clinica.
6. Se puede abrir la receta en PDF.
7. Recepcion o administracion registra el pago.
8. El sistema genera el ticket de cobro.

## 2. Arquitectura general

- Proyecto Django unico.
- Base de datos SQLite: `db.sqlite3`.
- Usuario personalizado: `cuentas.Usuario`.
- Aplicaciones principales:
  - `cuentas`: login, logout y roles.
  - `pacientes`: registro, edicion, baja logica y signos vitales.
  - `consulta`: cola del medico, historia clinica y receta PDF.
  - `facturacion`: pagos y tickets.

## 3. Roles del sistema

### Recepcion

- Ingresa al sistema.
- Registra pacientes.
- Edita pacientes.
- Da de baja pacientes y los reactiva.
- Agenda turnos solicitados por telefono, presencial o WhatsApp.
- Toma signos vitales.
- Registra pagos.
- Imprime tickets.

### Medico

- Ingresa al panel medico.
- Ve la cola de espera.
- Llama pacientes.
- Inicia la consulta.
- Guarda la historia clinica.
- Puede abrir la receta PDF.

### Administrador

- Tiene acceso general.
- En el menu lateral usa `Configuracion` para gestionar usuarios y medicos desde una pantalla simple.
- El admin tecnico de Django queda fuera del flujo normal de uso.
- Puede operar facturacion.

## 4. Logica funcional del sistema

### 4.1 Pacientes

- Los pacientes activos aparecen en `/pacientes/`.
- Se pueden editar.
- No se eliminan fisicamente por defecto.
- La baja se hace con `activo=False` para conservar historial, turnos y pagos.
- Los pacientes dados de baja aparecen en `/pacientes/inactivos/`.
- Desde esa lista se pueden reactivar.

### 4.2 Signos vitales y turnos

- Los turnos pueden cargarse por anticipado desde recepcion.
- El turno programado guarda canal de solicitud: `telefono`, `presencial` o `whatsapp`.
- El turno programado guarda fecha, hora, medico, motivo y observaciones de recepcion.
- Al agendar, el sistema valida que el medico no tenga otro turno en la misma fecha y hora.
- Al agendar, el sistema valida que el paciente no tenga otro turno en la misma fecha y hora.
- La vista de signos vitales crea un registro `SignosVitales`.
- Si el paciente ya tenia un turno programado para ese dia, se reutiliza ese turno y pasa a estado `espera`.
- Si no existia un turno programado, en ese paso se crea un `Turno` nuevo.
- El turno queda asignado a un medico.
- El numero de turno se genera en orden por dia.

### 4.2.1 Agenda operativa

- Desde la lista o ficha del paciente, recepcion puede usar `Agendar turno`.
- Si el paciente no existe, primero se crea y luego se agenda.
- La ficha del paciente muestra los proximos turnos programados.
- Desde la ficha se puede `Recepcionar` un turno programado para abrir la toma de signos del mismo turno.
- El estado `programado` se usa antes de la llegada del paciente.
- El estado `espera` se usa cuando el paciente ya fue recepcionado y esta listo para el medico.

### 4.3 Consulta medica

- El medico ve solo sus pacientes en espera.
- Puede llamar al paciente.
- Puede iniciar la consulta.
- Al guardar la historia clinica:
  - se crea `HistoriaClinica`
  - se guardan medicamentos de receta si fueron cargados
  - el turno pasa a estado `finalizado`

### 4.4 Receta PDF

- La receta PDF se genera desde una historia clinica ya guardada.
- Se puede abrir desde la ficha del paciente o desde la historia clinica.
- Usa los datos del consultorio definidos en configuracion.

### 4.5 Facturacion

- Solo recepcion y administrador pueden facturar.
- Facturacion muestra consultas finalizadas pendientes de cobro.
- Al registrar un pago se crea un `Pago`.
- Cada pago genera numero de recibo automatico.
- Si un turno ya tiene pago, el sistema redirige al ticket existente.

### 4.6 Configuracion operativa

- El acceso aparece solo para administradores.
- El menu `Configuracion` ya no envia al panel tecnico `/admin/`.
- La pantalla muestra dos accesos simples:
  - `Gestionar usuarios`
  - `Gestionar medicos`
- `Gestionar usuarios` permite crear y editar usuarios del sistema sin entrar al admin tecnico.
- `Gestionar medicos` permite crear y editar medicos con especialidad, matricula, estado activo y clave de acceso.
- Al editar un usuario o medico, la contraseña puede dejarse vacia para conservar la actual.

## 5. Configuracion para red local

El sistema esta pensado para correr en una PC servidor y abrirse desde otras computadoras de la misma red.

Datos actuales detectados en la PC servidor:

- Nombre del equipo: `DESKTOP-I9N9O2K`
- IP local actual: `192.168.1.105`

Acceso desde otras PCs:

- `http://192.168.1.105:8000/`

Importante:

- Si la IP cambia, hay que actualizar el script `iniciar_servidor_lan.bat`.
- Lo ideal es usar IP fija o reserva DHCP en el router.

## 6. Scripts operativos

### Iniciar servidor

Archivo: `iniciar_servidor_lan.bat`

Este script:

1. carga variables de entorno
2. aplica migraciones
3. inicia el servidor en `0.0.0.0:8000`

Variables relevantes dentro del script:

- `CLINICA_SECRET_KEY`
- `CLINICA_DEBUG`
- `CLINICA_ALLOWED_HOSTS`
- `CLINICA_CONSULTORIO_NOMBRE`
- `CLINICA_CONSULTORIO_DIRECCION`
- `CLINICA_CONSULTORIO_TELEFONO`
- `CLINICA_CONSULTORIO_EMAIL`
- `CLINICA_CONSULTORIO_CIUDAD`

### Backup de base de datos

Archivo: `backup_db.bat`

Este script:

1. crea la carpeta `backups/` si no existe
2. copia `db.sqlite3`
3. guarda el backup con fecha y hora

Ejemplo de nombre:

- `backups/db_2026-06-03_15-40-12.sqlite3`

## 7. Configuracion profesional actual

Se mejoro la configuracion para uso LAN mas serio:

- `DEBUG` ya no queda abierto por defecto.
- `ALLOWED_HOSTS` ya no usa `*` por defecto.
- `SECRET_KEY` puede venir desde entorno.
- Los datos del consultorio ya no estan duplicados en el codigo.
- Tickets y recetas usan la configuracion centralizada en `settings.py`.

## 8. Datos del consultorio

Todavia no se cargaron datos reales del consultorio.

Valores temporales actuales:

- Nombre: `Consultorio Medico`
- Direccion: `Direccion no configurada`
- Telefono: `Tel: no configurado`
- Email: `consultas@clinica.local`
- Ciudad: `Ciudad no configurada`

Cuando se tengan los datos reales, solo hay que modificar el script de inicio o cargar variables de entorno equivalentes.

## 9. Seguridad y operacion recomendada

- Usar una clave real en `CLINICA_SECRET_KEY`.
- Hacer backup diario de `db.sqlite3`.
- No usar `setup.py` como flujo normal.
- Verificar que solo la PC servidor ejecute el sistema.
- Mantener la carpeta `venv/` y dependencias del proyecto.

## 10. Comandos utiles

Verificacion rapida:

```powershell
venv\Scripts\python.exe manage.py check
```

Tests enfocados:

```powershell
venv\Scripts\python.exe manage.py test cuentas pacientes consulta facturacion
```

Servidor manual:

```powershell
venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

## 11. Pruebas implementadas

Actualmente el sistema tiene pruebas automaticas reales para estos casos:

### cuentas

- login de medico redirige al panel medico
- login de recepcion redirige a pacientes
- logout redirige al login sin romper plantilla
- administrador puede abrir la pantalla de configuracion
- recepcion no puede entrar a configuracion
- administrador puede crear medicos desde el formulario simple

### pacientes

- toma de signos crea `SignosVitales`
- toma de signos crea `Turno`
- recepcion puede agendar un turno con canal y medico
- no permite agendar el mismo horario para el mismo medico
- al tomar signos se reutiliza el turno programado del dia
- editar paciente actualiza datos
- baja logica deja `activo=False`
- lista principal oculta inactivos
- lista de inactivos los muestra
- reactivar paciente vuelve a dejarlo activo

### consulta

- guardar historia clinica crea `HistoriaClinica`
- guardar historia crea medicamentos de receta
- el turno termina en estado `finalizado`
- la receta PDF responde correctamente

### facturacion

- registrar pago crea `Pago`
- el primer recibo se genera desde `1000`
- un medico no puede acceder a facturacion

Estado actual de la suite enfocada:

- `19` tests OK

## 12. Prueba manual recomendada antes de puesta en marcha

1. Iniciar el sistema desde `iniciar_servidor_lan.bat`.
2. Entrar desde la PC servidor.
3. Entrar desde otra PC de la red usando `http://192.168.1.105:8000/`.
4. Login como recepcion.
5. Crear o editar paciente.
6. Agendar un turno futuro por telefono, presencial o WhatsApp.
7. Verificar que el turno aparezca en la ficha del paciente.
8. Recepcionar ese turno y tomar signos vitales.
9. Login como medico.
10. Llamar paciente, iniciar consulta y guardar historia.
11. Abrir receta PDF.
12. Volver a recepcion y registrar pago.
13. Abrir ticket e imprimir.
14. Probar baja y reactivacion de paciente.
15. Login como administrador y abrir `Configuracion`.
16. Crear o editar un usuario.
17. Crear o editar un medico.

## 13. Estado final actual

El sistema ya cuenta con:

- flujo funcional de recepcion, consulta y facturacion
- agenda previa de turnos con validacion de disponibilidad
- manejo de pacientes activos e inactivos
- receta PDF
- tickets de pago
- control de roles en facturacion
- scripts de inicio y backup
- pruebas automaticas de negocio sobre flujos criticos

Pendiente para cierre definitivo:

- cargar datos reales del consultorio
- definir rutina operativa de backups
- validar prueba manual completa en red local
