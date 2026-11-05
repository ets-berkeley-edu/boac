# boac/CLAUDE.md

Guidance for the Flask backend. The ground rules in the root `CLAUDE.md` (no commits, student-data protection, commenting, final checks) apply here too. Before changing an area that has a doc in `.claude/docs/`, read it.

## Where code goes

| Layer | Put here | Don't put here |
|---|---|---|
| `boac/api/*_controller.py` | Routes: read and validate request params, check access, call models/merged, return JSON | SQL, data-loch calls, business logic that other endpoints could reuse |
| `boac/api/util.py`, `*_api_utils.py` | Helpers shared by several controllers | |
| `boac/merged/` | Anything that combines BOA data (`boac/models/`) with data-loch or CalNet data. Most student data reaches the API through here | Flask request handling |
| `boac/models/` | SQLAlchemy models and queries against the `boac` DB | Data-loch queries |
| `boac/externals/` | Clients for external systems. All data-loch SQL lives in `data_loch.py` | Flask request handling |
| `boac/lib/` | Pure helpers with no route or model dependencies (`util.py`, `berkeley.py`, `http.py`) | |

A new controller module must be imported in `register_routes()` in `boac/routes.py`, or its routes won't exist.

## Writing a controller

Follow the shape of existing controllers, e.g. `boac/api/topic_controller.py`:

```python
@app.route('/api/topic/create', methods=['POST'])
@admin_required
def create_topic():
    params = request.json
    topic = params.get('topic', '').strip()
    if not topic:
        raise BadRequestError('Required parameters are missing.')
    topic = Topic.create_topic(topic)
    return tolerant_jsonify(topic.to_api_json())
```

- **Every route gets an access-check decorator** from `boac/api/decorators.py`, chosen with `.claude/docs/permissions.md`. Use the narrowest one that fits. Add an inline department or ownership check when the decorator alone isn't enough.
- **Return JSON with `tolerant_jsonify`** (`boac/lib/http.py`), not Flask's `jsonify`. Pass it dicts and lists (usually from a model's `to_api_json()`), never a model object.
- **JSON keys are camelCase** (`createdAt`, `peerAdvisingDepartmentId`). Python names stay snake_case. Do the conversion in `to_api_json()`.
- **Read params defensively.** Use `request.json` / `request.args` / `request.form` with `.get()`, and the converters in `boac/lib/util.py` (`to_bool_or_none`, `to_int_or_none`, `is_int`). Validate required fields, lengths, and types before calling anything else.
- **Route naming:** `/api/<resource>/...`, matching the neighboring routes in the same controller.

## Errors

Raise the classes in `boac/api/errors.py`. The handlers in `boac/api/error_handlers.py` turn them into JSON responses:

| Raise | Status | When |
|---|---|---|
| `BadRequestError(message)` | 400 | Missing or invalid input |
| `UnauthorizedRequestError` | 401 | Not logged in (decorators already handle this) |
| `ForbiddenRequestError` | 403 | Logged in, but not allowed to act on *this* resource |
| `ResourceNotFoundError` | 404 | The requested row doesn't exist or is soft-deleted |
| `InternalServerError` | 500 | A failure you've caught and want to report cleanly |

- Check for missing rows and raise `ResourceNotFoundError`. Don't let `None.attribute` turn into an unexpected 500.
- Error messages go to the browser. Keep them short and user-facing. Never include stack traces, SQL, config values, or another student's data.
- Decorators return 401 and inline checks usually raise 403. Tests assert the exact code, so be consistent with neighboring endpoints.

## Database access

- **`boac` DB:** use the SQLAlchemy models. For raw SQL, use `db.session.execute(text(sql), params)` with bound parameters (`:sid`), as in `boac/models/note.py`.
- **Data loch:** add a function to `boac/externals/data_loch.py` that calls `safe_execute_rds(sql, **params)`, with `%(name)s` placeholders. Schema names come from helpers like `student_schema()`. They're the only thing interpolated into the SQL string.
- **Never build SQL by interpolating request values** (f-strings, `%`, `+`). Always pass them as bound parameters.
- **Commit with `std_commit()`** from `boac/__init__.py`, not `db.session.commit()`. In tests it only flushes, so each test's changes roll back.
- **Soft delete is the norm.** Most tables have `deleted_at`. Filter it in queries, and set it rather than deleting rows unless the existing model hard-deletes.
- **Notes, note topics, and comments feed search.** They reach the data loch only through SQS change messages, so every write path must also call `sqs.send` (see `boac/models/note.py` and `comment.py`). If you change how they're written, read `.claude/docs/notes-and-search.md`.
- **Schema changes** follow `scripts/db/CLAUDE.md`.

## Caching

- `@stow('key_{arg}')` (`boac/models/json_cache.py`) caches a function's JSON result in the `json_cache` table, keyed by the formatted pattern. Use `for_term=True` for term-specific data.
- Cached values don't expire on their own. If you change data that a stowed function returns, clear the key (`json_cache.clear(key_like)`) or the stale value stays. The user session is the most common case: call `UserSession.flush_cached_user_session(user_id)` after changing anyone's roles or flags.
- Don't stow anything that depends on who is asking, unless the user is part of the key (e.g. `..._for_{owner_uid}`).

## Logging

- Use `app.logger`, with `.warning` for denied or unexpected requests and `.exception` inside `except` blocks.
- **Never log personal or sensitive data:** no SIDs, names, emails, note text, grades, tokens, or request bodies. Log IDs that aren't personal (note id, cohort id, user id) and counts instead.
- Some existing code logs SIDs (e.g. `boac/merged/advising_notes_reports.py`, `boac/api/cache_utils.py`), and `_safe_execute` logs query parameters at debug level. Don't copy those patterns into new code. Mention them to the developer if you're working nearby.

## Config and secrets

- New settings go in `config/default.py` with a safe default, and are read with `app.config['NAME']`.
- Secrets get a placeholder or `None` in `config/default.py`. Real values come from local or deployed config, never from the repo.
- Don't read or print the contents of `config/*-local.py`, `config/*.json`, or `BOAC_LOCAL_CONFIGS`. See `config/CLAUDE.md` for how config is loaded and how to add a setting.

## Python style

- Ruff enforces style (`ruff.toml`, line length 150). `tox -e lint-py` must pass.
- Single quotes, trailing commas in multi-line calls, and imports grouped stdlib / third-party / `boac` (Ruff sorts them).
- Every new `.py` file starts with the Regents license header (see the root `CLAUDE.md`).
- Private helpers in a module are prefixed with `_` and placed after the public functions that use them.
