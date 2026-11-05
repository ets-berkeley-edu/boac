# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is BOA

BOA (Berkeley Online Advising) is UC Berkeley's academic advising application. It aggregates student data from multiple campus systems and provides advising tools including notes, appointments, cohort management, degree progress tracking, and alerts.

## Ground rules

These apply to every task in this repo.

- **Never commit or push.** Make changes in the working tree and leave them uncommitted. The developer reviews and commits all work. If a task seems to call for a commit, stop and say so instead.
- **Accessibility is required: WCAG 2.2 AA.** Every frontend change must meet it. Treat accessibility as part of the change, not a follow-up. See `src/CLAUDE.md` for the specific rules and BOA's existing helpers.
- **Protect student data.** BOA handles FERPA-protected records, and this repo is public. Never put real student IDs (SIDs), names, grades, note text, or other personal data into code, fixtures, tests, logs, comments, or docs. Use synthetic values like the existing fixtures do. Never log secrets, tokens, or personal data.
- **Never read or copy local config overrides** (`config/*-local.py`, `config/*.json`, `.env*.local`, or anything under `BOAC_LOCAL_CONFIGS`). They can hold credentials. See `config/CLAUDE.md`.
- **Comment the code you write.** Add comments wherever they help the next reader understand intent: why the code exists, a non-obvious decision, or how a piece fits into the larger flow. Write them in plain, complete sentences. Aim for one or two sentences: long enough to be clear, short enough to skim. Don't restate what the code literally does.
- **Keep the guidance current.** If a change alters how something described in a `CLAUDE.md` file or a `.claude/docs/` doc works (a table, an endpoint's access rules, a flow, a convention), update that doc in the same change. If you notice a doc is already wrong, fix it or tell the developer. Don't leave it stale. Docs should describe how the code works now, not its history or known bugs.
- **Run the checks before you call work done.** When you finish a change, run all three and fix anything they report:

  ```bash
  tox -e lint-vue
  tox -e build-vue
  tox -e lint-py
  ```

  The frontend needs the Node version in `.nvmrc` (22). If `lint-vue` or `build-vue` fails with an error like `crypto.getRandomValues is not a function`, the shell is on an older Node. Run `nvm use` first.

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

See `boac/CLAUDE.md` for backend conventions: controllers, errors, database access, caching, and logging.

- **`boac/api/`** — Flask route controllers (one file per resource domain). Route registration happens in `boac/routes.py`.
- **`boac/models/`** — SQLAlchemy ORM models backed by the `boac` PostgreSQL database. These represent BOA-owned data (notes, cohorts, degree templates, users).
- **`boac/merged/`** — The central aggregation layer. Functions here combine data from the BOA database (`boac/models/`) with external SIS/data-warehouse data (`boac/externals/data_loch.py`). Most API responses for student data flow through this layer.
- **`boac/externals/`** — Clients for external systems: `data_loch.py` (read-only data warehouse with SIS/enrollment/grade data), `calnet.py` (LDAP-based UC Berkeley auth), `s3.py`/`sqs.py` (AWS).
- **`boac/lib/`** — Shared utilities: `analytics.py`, `berkeley.py` (term/dept constants), `util.py` (general helpers, including S3 attachment handling and search snippets).
- **`boac/factory.py`** — Flask app factory (`create_app()`). Entry point for WSGI is `application.py`.

### Frontend layers

See `src/CLAUDE.md` for frontend conventions and the accessibility rules.

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

Config files live in `config/` (`default.py`, `development.py`, `test.py`, and `bea.py` for the BEA browser tests). See `config/CLAUDE.md`. The `BOAC_ENV` environment variable selects the config. Tests set `BOAC_ENV=test` automatically. A `BOAC_LOCAL_CONFIGS` env var can point to an encrypted volume with local overrides.

### Testing approach

- **`tests`**: pytest unit tests. Tests in `tests/test_api/` test HTTP endpoints end-to-end against a real test database. `tests/conftest.py` sets up fixtures, mock AWS (via moto), and test users. Run a focused test with `pytest tests/path/to/test_file.py::ClassName::test_method`.
- **`bea`**: browser automation tests written using Selenium's Python API and run locally against a live BOA instance via Chromedriver (or Firefox/Safari).
- **Frontend**: there are no frontend unit tests. Frontend changes are verified with `tox -e lint-vue`, `tox -e build-vue`, and BEA.

See `tests/CLAUDE.md` for fixtures, test users, and how to write API tests.

### Local test database setup

Tests run against two local PostgreSQL databases (port taken from `PGPORT`). If `pytest` fails to connect, they probably haven't been created yet. This mirrors the setup in `.travis.yml`:

```bash
psql -c 'create database boac_test;'
psql -c 'create database boac_loch_test;'
psql boac_test -c 'create extension pg_trgm;'
psql boac_test -c 'create role boac superuser login; alter schema public owner to boac;'
psql boac_loch_test -c 'create extension pg_trgm;'
psql boac_loch_test -c 'alter schema public owner to boac;'
```

The test run loads `scripts/db/schema.sql` into `boac_test` and fakes the data loch by loading `fixtures/loch/loch.sql` into `boac_loch_test`.

## Team conventions

- **Branches** are named after the Jira ticket, e.g. `boac-1234` or `BOAC-1234`. Pull requests target `dev`.
- **Commit messages** (written by developers) start with the ticket, e.g. `BOAC-1234 - Short summary` or `BOAC-1234: short summary`.
- **License header.** Every new `.py` file starts with the Regents copyright header used throughout `boac/` and `tests/`. Use the current year in new files (`Copyright ©<current year>`). Don't change the year in existing files.
- **Schema changes** touch several files that must stay in sync. See `scripts/db/CLAUDE.md`.

## Domain docs

Background on specific areas of BOA. Read the relevant doc before changing code in that area.

- `.claude/docs/cohorts.md` — cohorts, cohort filters, and the admitted-students domain.
- `.claude/docs/notes-and-search.md` — advising notes, appointments, eForms, comments, attachments, and search.
- `.claude/docs/permissions.md` — user roles, the access-check decorators, and their frontend counterparts.
- `.claude/docs/degree-progress.md` — degree templates, student degree checks, requirements, and course assignment.
- `.claude/docs/peer-advising.md` — peer advising departments, peer advisors and managers, their notes, topics, templates, and reports.
- `.claude/docs/curated-groups.md` — hand-picked student groups, how they relate to cohorts, and bulk-adding students.
- `.claude/docs/alerts.md` — student alert types, how they're generated and dismissed, and where alert counts appear.
- `.claude/docs/student-profile.md` — the student page: how the profile is assembled from the data loch, what each role sees, and its frontend components.
- `.claude/docs/admitted-students.md` — CE3 admitted students: access checks, the OUA loch tables, admit endpoints and search, and how admits link to enrolled students.
- `.claude/docs/course-page.md` — the course (class section) page: its endpoint, the roster and Canvas data behind it, and how users reach it.
- `.claude/docs/admin-and-users.md` — managing BOA users and department memberships, the admin pages, service announcements, admin reports, and the config endpoint.
- `.claude/docs/data-refresh-and-terms.md` — the cache refresh job and its steps, `json_cache` / `@stow` keys, and how term IDs and the current term work.
- `.claude/docs/csv-exports.md` — every file download (cohort, group, and admit CSVs, the notes zip, admin and peer reports): access checks, columns, and the export UI.
- `.claude/docs/external-services.md` — the data loch, CalNet, S3, SQS, CAS, and Google Analytics: what BOA uses each for, the settings they read, and how tests fake them.
- `.claude/docs/frontend-shell.md` — app startup, layouts, router guards, axios error handling, the context store, demo mode, analytics, and how to wire up a new page.
- `.claude/docs/deployment.md` — how BOA is built and deployed to Elastic Beanstalk, how server config arrives, logs, CI, and which files change together on a version bump.
