# Data refresh and terms

BOA reads most student data live from the data loch, but it keeps some derived data in its own database: generated alerts, automated department memberships, cached CalNet records, cohort counts, and a key/value cache (`json_cache`). A single **refresh job** rebuilds that data. **Terms** decide what the job refreshes and what the UI treats as "current".

Key files: `boac/api/cachejob_controller.py` (endpoints), `boac/api/cache_utils.py` (job steps), `boac/models/job_progress.py` (job status), `boac/models/json_cache.py` (`@stow`), `boac/merged/sis_terms.py` and `boac/lib/berkeley.py` (terms), `src/lib/berkeley-utils.ts` (frontend term helpers), `scripts/refresh_current_term_cache.sh`, `application.py` (CLI).

Related docs: alert generation is in `.claude/docs/alerts.md`. Cohort count caching is in `.claude/docs/cohorts.md`. Curated group cleanup and alert-count keys are in `.claude/docs/curated-groups.md`. Membership automation and the API key are in `.claude/docs/permissions.md`. General `@stow` rules are in the Caching section of `boac/CLAUDE.md`.

## Triggering a refresh

| Method | Route / command | Auth | What it does |
|---|---|---|---|
| GET | `/api/admin/cachejob` | `@admin_required` | Returns `{progress}`: the `JobProgress` JSON, or `null` |
| GET | `/api/admin/cachejob/refresh?term=<id>` | `@admin_required` | `refresh_request_handler(term)`. `term` defaults to `current_term_id(use_cache=False)`. `term=all` loads every term |
| GET | `/api/admin/cachejob/continue` | `@admin_required` | `continue_request_handler()`. If the stored job is unfinished, starts `background_thread_refresh` for its stored `term_id` with `continuation=True`. Otherwise returns `{error, progress}` |
| GET | `/api/admin/cachejob/clear` | `@admin_required` | `JobProgress().delete()`; returns `{progressDeleted}` |
| CLI | `flask refresh_external_data` (`application.py`) | shell access | `refresh_request_handler(current_term_id())` (cached term lookup) |
| Script | `scripts/refresh_current_term_cache.sh <config file>` | `BOAC_API_KEY` from the config file | `curl`s `/api/admin/cachejob/refresh` with an `app-key` header and logs the response to `$LOGDIR` |

- **API key.** `@admin_required` passes when `_api_key_ok()` (`boac/api/decorators.py`) matches the `App-Key` header to `config['API_KEY']`. The default is `None`, which turns key access off. The script sends a hyphenated header because the AWS load balancer strips underscored ones. Key requests are also CSRF-exempt (`_enforce_csrf_protection` in `boac/routes.py`).
- **No in-app scheduler.** BOA has no cron, APScheduler, or `.ebextensions` job. Something outside the repo runs the script or calls the endpoint.
- **The endpoint returns right away.** The work runs on a daemon `Thread`. Poll `GET /api/admin/cachejob` for progress.

## Job flow (`boac/api/cache_utils.py`)

```
refresh_request_handler(term_id)
  → if a job_refresh_term row has start and no end: log an error and delete it
  → JobProgress().start({term_id}) → daemon Thread → background_thread_refresh(app, term_id)
      → refresh_current_term_index()      # clear 'current_term_index', re-stow it from the loch
      → load_term(term_id)
          term_id == 'all' → load_all_terms(): load_term() for each all_term_ids() entry,
                             recording each finished term in progress['terms_done']
          → refresh_alerts(term_id)                       # see alerts.md
          → only if term_id == current_term_id():
              refresh_department_memberships()            # rebuild automated memberships (permissions.md)
              disable_accounts_with_no_recent_activity()  # set disabled_at after LOGIN_INACTIVITY_THRESHOLD days (365)
              refresh_calnet_attributes()                 # clear 'calnet_user_for_uid_%', re-fetch for active users
              load_filtered_cohort_counts()               # clear 'cohort_filter_options_%', recompute every cohort (cohorts.md)
              update_curated_group_lists()                # drop SIDs missing from the loch (curated-groups.md)
      → JobProgress().end()
      on exception: JobProgress().update('An unexpected error occured: …') and re-raise; 'end' stays null
```

- A past term (`?term=2172`) refreshes only that term's alerts. The membership, CalNet, cohort, and curated-group steps run only for the current term.
- `refresh_current_term_index()` runs first on every job, so the rest of the job sees the loch's current term.
- `refresh_department_memberships()` calls `std_commit(allow_test_environment=True)`, so it really commits in tests.

## Job status (`boac/models/job_progress.py`)

`JobProgress` is not a table. It is one `json_cache` row with key `job_refresh_term` (`'job_' + REFRESH_TERM`):

```json
{"start": "YYYY-MM-DD HH:MM:SS", "end": null, "term_id": "2178",
 "steps": ["YYYY-MM-DD HH:MM:SS : About to refresh alerts for term 2178", "..."], "terms_done": ["2178"]}
```

- `start()` refuses (returns `False`) when a row has `start` and no `end`. `refresh_request_handler` avoids that by deleting an unfinished row first.
- `update()` appends a timestamped step and merges extra properties. It returns `False` when the job isn't running.
- `end()` stamps `end`. Timestamps use server local time (`datetime.now()`).

## `json_cache` and `@stow` (`boac/models/json_cache.py`)

Table: `json_cache (id, key varchar UNIQUE, json jsonb, created_at, updated_at)` (`scripts/db/schema.sql`).

- `@stow(key_pattern)` formats the pattern with the call's arguments (`get_args_dict` in `boac/lib/util.py`), returns the stored JSON if the key exists, and otherwise calls the function and inserts the result. A `None` result isn't stored.
- `for_term=True` prefixes the key with `term_{term name}-`, e.g. `term_Fall 2017-…`, using the call's `term_id` argument. `fetch(key, term_id)` reads the same form. No current code uses `for_term`.
- `fetch(key)` and `fetch_bulk(keys)` read without generating. `insert_row()` logs and ignores a unique-key conflict.
- `clear(key_like)` deletes rows matching a SQL `LIKE` pattern (`%` wildcard). Nothing expires on its own.

| Key | Stowed by | Cleared by |
|---|---|---|
| `current_term_index` | `sis_terms.get_current_term_index()` | `refresh_current_term_index()` at the start of every job |
| `boa_user_session_{user_id}` | `UserSession.load_user` (`boac/merged/user_session.py`) | `flush_cached_user_session()` (user admin endpoints), login, logout |
| `calnet_user_for_uid_{uid}` | `merged/calnet.get_calnet_user_for_uid`, `_get_calnet_users` (`insert_row`), `development_db` | `refresh_calnet_attributes()` (current-term job) |
| `calnet_user_for_csid_{csid}` | `merged/calnet.get_calnet_user_for_csid`, `_get_calnet_users` | nothing |
| `cohort_filter_options_*` (26 keys, incl. `…_academic_plans_for_{owner_uid}`, `…_grading_terms`) | `boac/lib/cohort_utils.py` | `load_filtered_cohort_counts()` (current-term job) |
| `alert_counts_curated_group_{group_id}_user_{viewer_id}` | `alert_counts_for_curated_group()` (`boac/api/util.py`) | `refresh_alerts()`, plus group edits and dismissals (see `curated-groups.md`) |
| `job_refresh_term` | `JobProgress` | `GET /api/admin/cachejob/clear`, or the next refresh if unfinished |

## Terms

A **term ID** is a 4-character string: century digit (`1` = 19xx, `2` = 20xx), two-digit year, season digit (`2` Spring, `5` Summer, `8` Fall). So `2178` is Fall 2017, `2182` is Spring 2018, and `1998` is Fall 1999. Numeric order is chronological.

| Helper (`boac/lib/berkeley.py`) | Behavior |
|---|---|
| `sis_term_id_for_name('Fall 2017')` | `'2178'`. Returns `None` for anything not matching `Spring|Summer|Fall YYYY` |
| `term_name_for_sis_id('2178')` | `'Fall 2017'`. Also maps season `0` to Winter |
| `previous_term_id(id)` | Spring → previous Fall (−4), otherwise −3 |
| `term_ids_range(earliest, latest)` | Every ID oldest → newest (Fall → +4, otherwise +3) |
| `academic_year_for_term_name(name)` | Fall YYYY → YYYY+1, otherwise YYYY, as a string |

| Helper (`boac/merged/sis_terms.py`) | Behavior |
|---|---|
| `current_term_name(use_cache=True)` / `current_term_id(use_cache=True)` | `CANVAS_CURRENT_ENROLLMENT_TERM`. When it's `'auto'` (default), uses `current_term_name` from the loch's `terms.current_term_index`, cached as `current_term_index`. `use_cache=False` reads the loch directly |
| `future_term_id()` | `CANVAS_FUTURE_ENROLLMENT_TERM`, or `future_term_name` from the same cached index when `'auto'` |
| `all_term_ids()` | Current term back to `CANVAS_EARLIEST_TERM` (default Fall 2016), newest first. Used by `term=all` refreshes |

- `data_loch.earliest_term_id()` is a different floor: `LEGACY_EARLIEST_TERM` (default Fall 2001). It bounds a student's enrollment history and the incompletes cohort filter.
- In tests, the loch fixture's `current_term_index` is Fall 2017 / Spring 2018, so `current_term_id()` is `'2178'`, `future_term_id()` is `'2182'`, and `all_term_ids()` is `['2178', '2175', '2172', '2168']` (`tests/test_merged/test_sis_terms.py`). Override the config with `override_config(app, 'CANVAS_CURRENT_ENROLLMENT_TERM', 'Spring 2021')`.

**Frontend.** `GET /api/config` (`boac/api/config_controller.py`) sends `currentEnrollmentTerm` (name), `currentEnrollmentTermId` (int), and `futureTermId` (int). `src/main.ts` loads it once into `useContextStore().config`. `src/lib/berkeley-utils.ts` mirrors the backend with `previousSisTermId`, `sisIdForTermName`, and `termNameForSisId`. None of them handle Winter (season `0`).

## Health check (`boac/api/status_controller.py`)

`GET /api/ping` has no auth decorator. It always returns 200 with `{app: true, db, data_loch, sqs}`. `db` runs `SELECT 1` on the BOA database, `data_loch` runs `SELECT 1` through `safe_execute_rds`, and `sqs` is `sqs_status()`, which only builds a boto client and doesn't call SQS. Check the booleans, not the status code. (`config.pingFrequency` in the frontend drives `/api/user/session_keep_alive`, not `/api/ping`.)

## Tests

- `tests/test_api/test_cachejob_controller.py`: auth on `/api/admin/cachejob`, including API key match, mismatch, and disabled.
- `tests/test_api/test_cache_utils.py`: `TestRefreshAlerts`, `TestRefreshCalnetAttributes`, `TestRefreshCurrentTermIndex`, `TestRefreshDepartmentMemberships`, `test_update_curated_group_lists`, `test_load_filtered_cohort_counts`.
- `tests/test_merged/test_sis_terms.py` and `tests/test_lib/test_berkeley.py` for term helpers.

## Gotchas

- **Term rollover waits for a refresh.** With `'auto'`, the current and future terms come from the cached `current_term_index`. When the loch moves to a new term, BOA keeps the old one until the next job clears the key. Open browser tabs keep the old `config` until reload.
- **Cached term lookups elsewhere.** `cohort_filter_options_grading_terms` bakes "(active)" / "(future)" labels into the cache. It's rebuilt only by a current-term refresh.
- **Overlapping runs.** A new refresh request deletes an unfinished job record and starts another thread. Check `GET /api/admin/cachejob` before starting one by hand.
- **A failed job never ends.** After an exception, `end` stays `null` and the last step holds the error. The next refresh request clears it.
- **Stow keys only see passed arguments.** `get_args_dict` skips default values, so every name in a key pattern must be passed explicitly. Arguments not in the pattern (e.g. `skip_expired_users` on `get_calnet_user_for_uid`) don't change the key, so the first caller's result is what everyone gets.
- **Don't change the term ID format.** Backend and frontend helpers parse it by position, and `alerts.key` values start with `{term_id}_`.
