# AGENTS.md

## Runtime
- This is a single Django project. Main settings live in `clinica/settings.py`; the root URLConf is `clinica/urls.py`.
- Use `venv\Scripts\python.exe` for commands on this Windows checkout if the virtualenv is not already activated.
- The app uses SQLite at `db.sqlite3`.

## Safe Commands
- Install deps: `venv\Scripts\python.exe -m pip install -r requirements.txt`
- Apply migrations: `venv\Scripts\python.exe manage.py migrate`
- Run dev server: `venv\Scripts\python.exe manage.py runserver`
- Lightweight verification: `venv\Scripts\python.exe manage.py check`
- Focused app test command: `venv\Scripts\python.exe manage.py test pacientes` (same pattern for `consulta`, `facturacion`, `cuentas`)

## Verification Reality
- `manage.py test` currently finds `0` tests, so `manage.py check` is the only meaningful fast verification already present.
- If you change request/response flow, also do a quick manual browser pass for login plus the affected workflow.

## Architecture That Matters
- `cuentas.Usuario` is the custom user model (`AUTH_USER_MODEL`); do not use Django's default `User` in migrations, relations, or fixtures.
- Root `/` redirects to `/pacientes/`.
- Real business flow is `pacientes` -> `consulta` -> `facturacion`.
- `pacientes` handles patient registry and reception intake.
- `pacientes.signos_vitales` creates both `SignosVitales` and the `consulta.Turno` sent to a doctor.
- `consulta` handles the doctor queue, consultation, `HistoriaClinica`, and prescription line items.
- `facturacion` handles payment/ticket flow tied `OneToOne` to `consulta.Turno`.

## Repo-Specific Gotchas
- `setup.py` is not packaging metadata here. Running `python setup.py` rewrites `requirements.txt`, runs migrations, and seeds a default admin user (`admin` / `admin123`). Do not run it for normal development.
- Templates are centralized under root `templates/`, not inside each app.
- `consulta/generador_receta.py` exists, but no current view imports or calls it.
- `pacientes/views.py` renders `pacientes/detalle.html` and `consulta/views.py` renders `consulta/ver_historia.html`, but those template files are not present in `templates/` right now.

## Settings Quirks
- `DEBUG = True` and `ALLOWED_HOSTS = ['*']` are committed in `clinica/settings.py`; avoid treating this repo as production-hardened.
- Static files use `static/`; uploaded/generated files use `media/`, which is gitignored.
