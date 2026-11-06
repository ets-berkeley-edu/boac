# config/CLAUDE.md

Guidance for BOA's Flask configuration. The ground rules in the root `CLAUDE.md` apply here too, especially: never read or copy local config overrides.

## How config is loaded

`create_app()` (`boac/factory.py`) calls `load_configs()` (`boac/configs.py`), which layers files in this order. Later files override earlier ones:

1. `config/default.py`, always.
2. `config/{BOAC_ENV}.py`. `BOAC_ENV` defaults to `development` when unset. If no such module exists, the step is skipped silently.
3. `{BOAC_ENV}-local.py` from the `BOAC_LOCAL_CONFIGS` directory if that variable is set, otherwise from `config/` (the path `../config` is resolved against the `boac/` package). It is loaded with `silent=True`, so a missing or misnamed file is ignored without warning.

Finally `app.config['BOAC_ENV']` is set to the environment name.

- Only UPPERCASE names in these files become settings, which is why helpers like `_db_port` in `test.py` are private lowercase names.
- Environment variables are not mapped into `app.config`. The loader itself reads only `BOAC_ENV` and `BOAC_LOCAL_CONFIGS`. A config file may read the environment itself, as `test.py` does with `PGPORT`.
- `BOAC_LOCAL_CONFIGS` replaces the local-file location rather than adding to it. When it's set, `config/{BOAC_ENV}-local.py` is not loaded.
- `tests/conftest.py` sets `BOAC_ENV=test` and `bea/conftest.py` sets `BOAC_ENV=bea` before creating the app. With `bea`, `create_app()` skips route registration.

## Tracked files

| File | Purpose |
|---|---|
| `default.py` | Every app setting with a safe default. The only place a new setting is declared. |
| `development.py` | Local dev: `DEBUG`, demo mode, and the Vite dev-server settings (`INDEX_HTML`, `VUE_LOCALHOST_BASE_URL`). |
| `test.py` | pytest: test databases on `PGPORT`, CSRF off, some alerts off, test log file. |
| `bea.py` | Settings for the BEA browser tests (`bea/`), not the Flask app: browser, timeouts, test term, placeholder admin credentials. |

Everything else in `config/` is local and git-ignored. Check with `git ls-files config/` and `ls config/`, never by opening the files.

## Adding a setting

- Declare it in `default.py`, keeping the alphabetical order, with a safe default and a one-line comment when the name doesn't explain itself (units, what `None` means).
- Read it with `app.config['NAME']`. Because every setting has a default, a missing key is a bug, so don't use `.get()` to paper over it.
- Override it in `test.py` only when the whole test suite needs a different value. For one test, use `override_config(app, 'NAME', value)` from `tests/util.py`.
- **Frontend access** goes through `app_config()` in `boac/api/config_controller.py` (`GET /api/config`). Add a camelCase key there and the matching field to `BoaConfig` in `src/lib/types.ts`. `src/main.ts` loads it into `useContextStore().config`.
- `/api/config` has no access decorator, so anyone can read it, and the admin Flight Deck (`src/views/FlightDeck.vue`) lists every key. Never add a secret, credential, internal hostname, or personal data to it.

## Secrets

These settings in `default.py` hold secrets or credentials. Each has `None` or an obvious placeholder there. Real values exist only in local or deployed config:

- `SECRET_KEY` (session cookie signing), `API_KEY`, `CSRF_BYPASS_KEY`
- `DEVELOPER_AUTH_PASSWORD`, `LDAP_BIND`, `LDAP_PASSWORD`
- `SQLALCHEMY_DATABASE_URI`, `DATA_LOCH_RDS_URI` (connection strings with passwords)
- `AWS_APP_ROLE_ARN` (contains an AWS account ID). There are no AWS access-key settings; `boac/externals/aws.py` assumes this role.

Rules:

- **Never read, print, or copy** `config/*-local.py`, `config/*.json`, or anything under `BOAC_LOCAL_CONFIGS`. `.gitignore` excludes `config/*-local.py`, `config/*-local.conf`, `config/*.json`, `boac/.env`, and `.env*.local`.
- **Never put a real secret in a tracked file**, including `test.py` and `bea.py`. New secret settings default to `None` and the code treats `None` as "off", as `_api_key_ok()` (`boac/api/decorators.py`) and `_csrf_bypass_key_ok()` (`boac/routes.py`) do.
- Add `# noqa: S105` to a placeholder string password, as `default.py` does, so Ruff's hard-coded-password check passes. Use it only on placeholders.

## Feature flags

Boolean flags are named `<FEATURE>_ENABLED` or `<FEATURE>_AVAILABLE` and checked with a plain `if app.config['NAME']:`. Examples:

- `ALERT_WITHDRAWAL_ENABLED`, `ALERT_NO_ACTIVITY_ENABLED` (checked in `boac/models/alert.py`)
- `DEVELOPER_AUTH_ENABLED` (`boac/api/auth_controller.py`), sent to the frontend as `devAuthEnabled`
- `DEMO_MODE_AVAILABLE` (`boac/api/user_controller.py`), sent to the frontend as `isDemoModeAvailable`

## Gotchas

- **Tests differ from dev.** `test.py` sets `WTF_CSRF_ENABLED = False`, so most API tests never exercise CSRF. It turns off `ALERT_INFREQUENT_ACTIVITY_ENABLED` and `ALERT_WITHDRAWAL_ENABLED` (tests re-enable them with `override_config`) and raises `COHORT_FILTER_ACADEMIC_STANDING_YEARS_CUTOFF` from 5 to 100 years. `DEVELOPER_AUTH_ENABLED` stays off; the `fake_auth` fixture overrides it per login.
- **A local file can override tests.** A `test-local.py` is loaded during pytest like any other env's local file, and can silently change test database URIs or flags.
- **Settings that move together:** `DEVELOPER_AUTH_ENABLED` with `DEVELOPER_AUTH_PASSWORD` (the password also powers admin "become user"); `CAS_SERVER` with `CAS_LOGOUT_URL`; `INDEX_HTML` with `VUE_LOCALHOST_BASE_URL`; `WTF_CSRF_CHECK_DEFAULT = False` relies on the explicit check in `boac/routes.py`, so don't flip it without reading `_enforce_csrf_protection()`.
- **`API_KEY` does two things:** a matching `App-Key` header passes most access decorators in `boac/api/decorators.py` (including `@admin_required`) and also skips CSRF.
- `LOGGING_LEVEL` defaults to `DEBUG`, the level at which `_safe_execute` in `boac/externals/data_loch.py` logs SQL and its parameters. Any new debug logging is written to the log by default, so it must not include personal data.
