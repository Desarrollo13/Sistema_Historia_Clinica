# Manual del Sistema de Historia Clinica

## 1. Objetivo

Este sistema permite trabajar la atencion de un consultorio medico en red local desde varias computadoras.

Flujo principal:

1. Recepcion registra o busca al paciente.
2. Recepcion toma signos vitales.
3. El sistema crea un turno y lo envia al medico.
4. El medico atiende al paciente y completa la historia clinica.
5. Se puede abrir la receta en PDF.
6. Recepcion o administracion registra el pago.
7. El sistema genera el ticket de cobro.

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
- Puede usar el admin de Django.
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

- La vista de signos vitales crea un registro `SignosVitales`.
- En el mismo paso se crea un `Turno`.
- El turno queda asignado a un medico.
- El numero de turno se genera en orden por dia.

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

### pacientes

- toma de signos crea `SignosVitales`
- toma de signos crea `Turno`
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

- `13` tests OK

## 12. Prueba manual recomendada antes de puesta en marcha

1. Iniciar el sistema desde `iniciar_servidor_lan.bat`.
2. Entrar desde la PC servidor.
3. Entrar desde otra PC de la red usando `http://192.168.1.105:8000/`.
4. Login como recepcion.
5. Crear o editar paciente.
6. Tomar signos vitales.
7. Login como medico.
8. Llamar paciente, iniciar consulta y guardar historia.
9. Abrir receta PDF.
10. Volver a recepcion y registrar pago.
11. Abrir ticket e imprimir.
12. Probar baja y reactivacion de paciente.

## 13. Estado final actual

El sistema ya cuenta con:

- flujo funcional de recepcion, consulta y facturacion
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
