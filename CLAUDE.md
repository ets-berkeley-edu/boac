# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is BOA

BOA (Berkeley Online Advising) is UC Berkeley's academic advising application. It aggregates student data from multiple campus systems and provides advising tools including notes, appointments, cohort management, degree progress tracking, and alerts.

## Commands

### Backend (Python/Flask)

```bash
flask run --debugger          # Run dev server
flask initdb                  # Initialize database schema

tox -e test                   # Run all pytest tests
pytest tests/test_api/test_notes_controller.py  # Run a single test file
pytest tests/test_api/test_notes_controller.py::TestNotes::test_foo  # Run a single test
tox -e lint-py                # Lint with Ruff
```

### Frontend (Vue 3 / TypeScript)

```bash
npm run serve-vue             # Vite dev server
npm run build-vue             # Production build to dist/static
npm run lint-vue              # ESLint
npm run lint-vue-fix          # ESLint with auto-fix
npm run oxlint                # Oxlint static analysis
```

### Run everything (lint + tests + build)

```bash
tox -p                        # Run all tox envs in parallel
```

## Architecture

### Backend layers

- **`boac/api/`** — Flask route controllers (one file per resource domain). Route registration happens in `boac/routes.py`.
- **`boac/models/`** — SQLAlchemy ORM models backed by the `boac` PostgreSQL database. These represent BOA-owned data (notes, cohorts, degree templates, users).
- **`boac/merged/`** — The central aggregation layer. Functions here combine data from the BOA database (`boac/models/`) with external SIS/data-warehouse data (`boac/externals/data_loch.py`). Most API responses for student data flow through this layer.
- **`boac/externals/`** — Clients for external systems: `data_loch.py` (read-only data warehouse with SIS/enrollment/grade data), `calnet.py` (LDAP-based UC Berkeley auth), `s3.py`/`sqs.py` (AWS).
- **`boac/lib/`** — Shared utilities: `analytics.py`, `background.py` (scheduler), `berkeley.py` (term/dept constants).
- **`boac/factory.py`** — Flask app factory (`create_app()`). Entry point for WSGI is `application.py`.

### Frontend layers

- **`src/api/`** — Axios-based API client modules (one per backend domain). All HTTP calls go through here.
- **`src/views/`** — Page-level Vue components, organized by feature area.
- **`src/components/`** — Reusable components, organized in subdirectories by feature.
- **`src/stores/`** — Pinia stores for shared state (`context.ts` holds current user and global config).
- **`src/lib/`** — Frontend utilities; `types.ts` has shared TypeScript types, `boa-user.ts` has permission-check helpers.
- **`src/router.ts`** — Vue Router configuration.

### Databases

Two PostgreSQL databases:
- **`boac`** — Application-owned data (notes, cohorts, users, degree progress, appointments).
- **`boac_loch_test`** (test only) / data loch in production — Read-only external data warehouse with SIS, enrollment, and grade data. Queried via `boac/externals/data_loch.py`.

### Configuration

Config files live in `config/` (`default.py`, `development.py`, `test.py`). The `BOAC_ENV` environment variable selects the config. Tests set `BOAC_ENV=test` automatically. A `BOAC_LOCAL_CONFIGS` env var can point to an encrypted volume with local overrides.

### Testing approach

- **`tests`**: pytest unit tests. Tests in `tests/test_api/` test HTTP endpoints end-to-end against a real test database. `tests/conftest.py` sets up fixtures, mock AWS (via moto), and test users. Run a focused test with `pytest tests/path/to/test_file.py::ClassName::test_method`.
- **`bea`**: browser automation tests written using Selenium's Python API and run locally against a live BOA instance via Chromedriver (or Firefox/Safari).
