# scripts/db/CLAUDE.md

Guidance for changes to the `boac` database schema. The ground rules in the root `CLAUDE.md` apply here too.

## Files that must stay in sync

`schema.sql` is the full, current schema. It's what builds the test database and new environments. Existing environments are upgraded by running a one-off migration script instead. So every schema change needs both, plus the model:

| File | What to change |
|---|---|
| `scripts/db/migrate/<year>/<YYYYMMDD>-BOAC-<ticket>/<description>.sql` | A new migration that changes an existing database, e.g. `migrate/2026/20260105-BOAC-5253/pre_deploy_01_add_column_authorized_users_disabled_at.sql`. Use today's date and the Jira ticket number. |
| `scripts/db/schema.sql` | Make the same change so a fresh database ends up identical to a migrated one. |
| `scripts/db/drop_schema.sql` | Add or remove the matching `DROP` statement when you add or remove a table, type, sequence, or index. Column changes don't need an edit here. |
| `boac/models/<model>.py` | Update the SQLAlchemy model (columns, constructor, `to_api_json`, `__repr__`) to match. |

For example, BOAC-6790 dropped two indexes and touched the migration, `schema.sql`, `drop_schema.sql`, and `boac/models/note.py` together.

## Writing a migration

- Wrap the statements in a transaction (`BEGIN;` … `COMMIT;`), like the existing scripts.
- Make it safe to re-run where Postgres allows it: `IF EXISTS` / `IF NOT EXISTS`.
- Name files by what they do. Use the prefixes `pre_deploy_01_`, `pre_deploy_02_`, … or `post_deploy_01_` when the order relative to the code deploy matters, e.g. a new column must exist before code that reads it ships.
- Add a short SQL comment (`--`) when the reason for the change isn't obvious from the statement, e.g. why a backfill uses a particular default.
- Data migrations that insert rows (e.g. a new peer advising department) may contain institutional reference data such as department codes and names, but never student data.
- Migration scripts don't carry the license header. `schema.sql` and `drop_schema.sql` already have one, so leave it alone.

## Checking the change

The test suite builds `boac_test` from `schema.sql`, so running the tests that cover the affected model catches most mismatches between `schema.sql` and the model:

```bash
pytest tests/test_models
```

Nothing automatically checks that the migration produces the same result as `schema.sql`. Read them side by side before calling the change done.

`schema.sql` has already drifted in places, e.g. the `degree_progress_courses` unique constraint still reflects the version before BOAC-4199, and the BOAC-6781 foreign-key indexes are missing. Before relying on a constraint or index in `schema.sql`, check the later migrations for the same table. Don't fix unrelated drift as part of another change; mention it to the developer instead.
