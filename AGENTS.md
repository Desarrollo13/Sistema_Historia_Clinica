# AGENTS.md

## Runtime
- Single Django project. Settings: `clinica/settings.py`; root URLs: `clinica/urls.py`.
- Use `venv\Scripts\python.exe` on this Windows checkout if the venv is not already activated.
- SQLite database lives at `db.sqlite3`.
- Templates are centralized under root `templates/` via `TEMPLATES['DIRS']`, even though `APP_DIRS` is also enabled.

## Safe Commands
- Install deps: `venv\Scripts\python.exe -m pip install -r requirements.txt`
- Apply migrations: `venv\Scripts\python.exe manage.py migrate`
- Run dev server: `venv\Scripts\python.exe manage.py runserver`
- Fast verification: `venv\Scripts\python.exe manage.py check`
- App-level tests: `venv\Scripts\python.exe manage.py test pacientes consulta facturacion cuentas`
- Single app test: `venv\Scripts\python.exe manage.py test pacientes` (same pattern for the other apps)

## Architecture That Matters
- `cuentas.Usuario` is the custom user model (`AUTH_USER_MODEL`); do not use Django's default `User` in models, migrations, or fixtures.
- Root `/` redirects to `/pacientes/`.
- Main workflow is `pacientes` -> `consulta` -> `facturacion`.
- `pacientes.signos_vitales` creates both `SignosVitales` and the linked `consulta.Turno`; reception intake is what feeds the doctor queue.
- `consulta` owns the doctor panel, `Turno`, `HistoriaClinica`, `RecetaMedicamento`, and the PDF prescription endpoint.
- `facturacion.Pago` is `OneToOne` with `consulta.Turno`; payment is expected only after the turn reaches `estado='finalizado'`.

## Roles And Routing
- Role gating is implemented in `cuentas/views.py` with `rol_requerido`, `solo_medico`, and `solo_recepcion`.
- Login redirects are role-based: doctors go to `/consulta/panel/`; everyone else goes to `/pacientes/`.
- `facturacion` views allow `recepcion` and admins; `consulta` views are doctor-only.

## Repo-Specific Gotchas
- Do not run `python setup.py` for normal work. In this repo it is a bootstrap script that rewrites `requirements.txt`, installs packages, runs migrations, and seeds `admin` / `admin123`.
- `consulta/views.py` actively imports and uses `consulta/generador_receta.py`; changes to prescription data should be checked against the PDF output too.
- Media is served from `media/` and wired in `clinica/urls.py`; generated files are not committed.

## Settings Quirks
- `DEBUG` defaults to off unless `CLINICA_DEBUG` is set; `ALLOWED_HOSTS` comes from `CLINICA_ALLOWED_HOSTS` and otherwise defaults to `127.0.0.1`, `localhost`, and the machine hostname.
- Consultorio identity for tickets/recipes is environment-driven via `CLINICA_CONSULTORIO_*` settings in `clinica/settings.py`.
