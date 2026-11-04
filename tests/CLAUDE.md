# tests/CLAUDE.md

Guidance for the pytest suite. The ground rules in the root `CLAUDE.md` apply here too. See its "Local test database setup" section if tests can't connect to Postgres.

## How the test run is set up

- `BOAC_ENV=test` selects `config/test.py`, which points at the local `boac_test` and `boac_loch_test` databases.
- `boac_test` is built from `scripts/db/schema.sql` and seeded from `fixtures/development_db/` (test users, departments, topics, cohorts, curated groups) by `boac/models/development_db.py`.
- The data loch is faked: the session-scoped `fake_loch` fixture in `conftest.py` loads `fixtures/loch/loch.sql` and the `fixtures/loch/student_*.json` files into `boac_loch_test`.
- AWS is mocked with moto (`fake_aws` in `conftest.py`), including a fake SQS queue. Helpers in `tests/util.py` create mock S3 buckets for attachments.
- To emulate the SQS + Lambda searchlight-cdc process, search tests rebuild the loch search indexes with `refresh_loch_note_search_index`, `refresh_loch_appointment_search_index`, and `refresh_loch_eform_search_index` from `tests/util.py`. Each takes a list of records to index and a list to remove (`notes`/`deleted_notes`, or `comments`/`deleted_comments`). Set `created_at` before indexing, because the index computes `age_days` from it.

## Writing API tests

API tests in `tests/test_api/` call real endpoints through the Flask test client against the test databases. Follow the pattern of existing files such as `test_topic_controller.py`:

- **One class per endpoint or behavior** (e.g. `TestGetTopics`, `TestCreateTopic`), with a small classmethod helper that calls the API and asserts the expected status code.
- **Log in with `fake_auth.login(uid)`.** It uses developer auth to start a session as that user.
- **Test users are UID constants at the top of the file**, e.g. `coe_advisor_uid = '1133399'`. Reuse the existing constants and users from `fixtures/development_db/test_users.json` rather than inventing new UIDs. `.claude/docs/permissions.md` lists which roles they represent.
- **Cover access control first.** Most test classes start with `test_not_authenticated` (expects 401) and a test for each kind of user who should be denied, before testing the happy path.
- **Docstrings** on each test describe the behavior in one short sentence, e.g. `"""Denies anonymous access."""`.
- Shared helpers for cohorts and curated groups live in `tests/test_api/api_test_utils.py`.

## Test data

All data in `fixtures/` is synthetic. Keep it that way:

- Never copy real SIDs, names, grades, notes, or other student data from the data loch, production, or a bug report into fixtures or tests.
- When a test needs new data, add synthetic rows that follow the existing fixture formats.
- Don't print or log student-shaped data in tests beyond what an assertion needs.

## Running tests

```bash
tox -e test                                        # full suite
pytest tests/test_api/test_topic_controller.py     # one file
pytest tests/test_api/test_topic_controller.py::TestCreateTopic::test_create_topic   # one test
```
