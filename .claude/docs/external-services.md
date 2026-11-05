# External services

BOA reads student data from the **data loch** (a read-only Postgres warehouse), looks people up in **CalNet** (LDAP), stores and serves files in **S3**, and announces note and comment changes on **SQS**. Logins go through **CAS**, and the frontend reports usage to **Google Analytics**. BOA has no Canvas, SIS API, or email client: Canvas and SIS data arrive through loch tables, and `boac/lib/http.py`'s `request()` wrapper has no callers.

Key files: `boac/externals/data_loch.py`, `boac/externals/calnet.py` and `boac/merged/calnet.py`, `boac/externals/aws.py`, `boac/externals/s3.py`, `boac/externals/sqs.py`, `boac/api/auth_controller.py` (CAS), `src/lib/ga.ts`, `boac/lib/mockingdata.py` and `boac/lib/mockingbird.py` (test fakes), `tests/conftest.py`, `tests/util.py`.

Related docs: SQL rules are in the Database access section of `boac/CLAUDE.md`. The search pipeline that consumes SQS is in `.claude/docs/notes-and-search.md`. `@stow` and the CalNet refresh are in `.claude/docs/data-refresh-and-terms.md`. Test setup is in `tests/CLAUDE.md`. Adding config settings is in `config/CLAUDE.md`.

| Service | Client | Used for | Config settings | Test fake |
|---|---|---|---|---|
| Data loch | `data_loch.py` (psycopg2 pool) | Student, enrollment, admit, legacy note and search data | `DATA_LOCH_RDS_URI`, `DATA_LOCH_MAX_CONNECTIONS`, `DATA_LOCH_*_SCHEMA`, `LEGACY_EARLIEST_TERM` | Local `boac_loch_test` DB loaded from `fixtures/loch/loch.sql`, plus `@fixture` CSVs |
| CalNet LDAP | `externals/calnet.py` (ldap3), `merged/calnet.py` | Names, emails, CSIDs, titles, and departments for UIDs and CSIDs | `LDAP_HOST`, `LDAP_BIND`, `LDAP_PASSWORD` | `MockClient` on ldap3 `MOCK_SYNC` with `fixtures/calnet_*.json`, plus pre-seeded `json_cache` rows |
| AWS STS | `externals/aws.py` | Assumed-role credentials for every S3 and SQS client | `AWS_APP_ROLE_ARN` | moto (`fake_aws`) |
| S3 | `externals/s3.py` (boto3, smart_open) | Note, comment, and template attachments; legacy SIS and EOP attachments; student photos | `AWS_REGION`, `DATA_LOCH_S3_*`, `PHOTO_SIGNED_URL_EXPIRES_IN_SECONDS` | moto buckets from `tests/util.py` |
| SQS | `externals/sqs.py` (boto3) | Change messages for notes, note topics, and comments | `AWS_SQS_QUEUE_URL`, `AWS_REGION` | moto queue from `fake_aws` |
| CAS | `auth_controller.py` (python-cas `CASClientV3`) | SSO login and logout URLs, ticket validation | `CAS_SERVER` | `mock.patch.object(cas.CASClientV3, 'verify_ticket')` in `test_auth_controller.py` |
| Google Analytics | `src/lib/ga.ts` (vue-gtag) | Frontend usage events | `GA_MEASUREMENT_ID` (sent as `gaMeasurementId` by `/api/config`) | None; off when the setting is empty |

## Data loch (`boac/externals/data_loch.py`)

- **Connection.** `safe_execute_rds(sql, **params)` builds a module-global psycopg2 `ThreadedConnectionPool(1, DATA_LOCH_MAX_CONNECTIONS, DATA_LOCH_RDS_URI)` on first use. `cursor_from_pool()` borrows a connection, yields a `DictCursor`, and returns the connection in `finally`. The pool doesn't wait: when every connection is in use, `getconn()` raises. The code sets no connect or statement timeout and doesn't retry.
- **Errors.** `_safe_execute()` catches `psycopg2.Error`, logs it with `app.logger.exception` (including the SQL), and returns `None`. Callers must treat `None` as failure, not as "no rows". On success it returns a list of plain dicts and logs row count, timing, SQL, and params at debug level.
- **Writing a query.** Use `%(name)s` placeholders and pass values as keyword arguments, e.g. `safe_execute_rds(sql, sid=sid)`. Only schema names are interpolated, from helpers such as `student_schema()`, `sis_schema()`, `terms_schema()`, `oua_schema()`, and `boa_cdc_schema()` (each returns one `DATA_LOCH_*_SCHEMA` setting). Follow `boac/CLAUDE.md` for the rest.
- **Not every function is loch-only.** A few search and cohort queries first read the `boac` DB through `db.session` (advisor UIDs by department, curated-group SIDs) and pass the result into the loch query as a bound array.
- **Caching.** Nothing in this module caches. Callers that need it use `@stow` (e.g. `sis_terms.get_current_term_index()`).
- **Health.** `GET /api/ping` runs `SELECT 1` through `safe_execute_rds` and reports `data_loch: rows is not None`.

**Tests.** `config/test.py` points `DATA_LOCH_RDS_URI` at the local `boac_loch_test` database. The session-scoped, autouse `fake_loch` fixture runs `fixtures/loch/loch.sql` once. That file creates the loch schemas under their default `DATA_LOCH_*_SCHEMA` names and inserts synthetic rows. Each `fixtures/loch/student_<key>.json` file is bound to the `:<key>` parameter in that SQL (e.g. `:athletics_profile_<sid>`). Search tests write extra rows with the `refresh_loch_*_search_index` helpers in `tests/util.py`.

## CSV fixtures (`boac/lib/mockingdata.py`)

In `test` and `demo` (`BOAC_ENV`), a loch function decorated with `@fixture('loch/<pattern>.csv')` returns rows from a CSV under `FIXTURES_PATH` (default `BASE_DIR/fixtures`) instead of running its SQL. The pattern is filled from the call's arguments with `fill_pattern_from_args`. Two functions use it: `get_sis_section` and `get_sis_section_enrollments`, reading `fixtures/loch/sis_section_{term_id}_{sis_section_id}.csv` and `sis_section_enrollments_….csv`.

- `MockRows` parses the CSV with pandas and round-trips it through JSON. Only `ldap_uid`, `sis_section_num`, and `uid` stay strings. Other numeric-looking columns become numbers.
- If the CSV doesn't exist, the function returns `None`. It does not fall back to the SQL.
- A test can swap in its own rows: `with register_mock(data_loch.get_sis_section, MockRows(io.StringIO('col1,col2\n…'))):` (see `tests/test_externals/test_data_loch.py`). Mocks stack last-in-first-out.
- To add one: decorate the function, then add a synthetic CSV whose header matches the query's columns.

## CalNet (`boac/externals/calnet.py`, `boac/merged/calnet.py`)

- **Client.** `calnet.client(app)` returns `MockClient` in `test` and `demo`, and `Client` otherwise. `Client` connects to `LDAP_HOST` on port 636 over SSL with `ssl.CERT_REQUIRED`, binds with `LDAP_BIND` / `LDAP_PASSWORD`, and uses the `SAFE_SYNC` strategy. It opens a new connection per batch. No timeout or retry is configured.
- **Lookups.** `search_uids(uids, search_expired=False)` and `search_csids(...)` drop non-numeric IDs and query in batches of `BATCH_QUERY_MAXIMUM` (500). The filter is `objectclass=person`, an OR of the IDs, and either `ou=people` / `ou=advcon people` or, with `search_expired=True`, `ou=expired people`. `_attributes_to_dict` maps LDAP attributes through `SCHEMA_DICT` (uid, csid, names, emails, title, `departmentNumber`, `berkeleyEduPrimaryDeptUnit`, affiliations) and sets `expired`.
- **Merged layer.** `get_calnet_user_for_uid` and `get_calnet_user_for_csid` search active people first, then expired ones, and return a camelCase feed (`firstName`, `lastName`, `csid`, `departments`, `isExpiredPerLdap`, …). `departments` comes from the primary dept unit, falling back to `departmentNumber`, named via `BERKELEY_DEPT_CODE_TO_NAME`. `skip_expired_users=True` searches active people only. With `force_feed=False`, a miss returns `None`. Otherwise a miss returns a feed with only the ID filled in.
- **Caching.** Single lookups are `@stow`ed as `calnet_user_for_uid_{uid}` / `calnet_user_for_csid_{csid}`. `get_calnet_users_for_uids` / `_for_csids` read cached rows with `fetch_bulk`, search LDAP for the rest (active OUs only), and `insert_row` each result, including empty feeds for misses. The current-term refresh job clears and rebuilds the UID keys for active users (`refresh_calnet_attributes()`).
- **Errors.** Neither layer catches ldap3 exceptions, so an LDAP outage raises to the caller.

**Tests.** `MockClient` builds an ldap3 server from `fixtures/calnet_server_info.json` and `calnet_server_schema.json`, binds anonymously with `MOCK_SYNC`, and loads entries from `fixtures/calnet_search_entries.json`. Every entry is under `ou=people`, so expired searches find nothing. Most test users never reach the mock: `development_db._create_users()` and `user_factory(has_calnet_record=True)` insert `calnet_user_for_uid_*` rows into `json_cache` first.

## AWS credentials (`boac/externals/aws.py`)

`get_session()` calls STS `assume_role` on `AWS_APP_ROLE_ARN` (900-second credentials) using the default boto3 credential chain, and returns a `boto3.Session`. `s3._get_client()` and `sqs._get_client()` call it every time, so each S3 or SQS operation does a fresh STS call. Clients use boto3's default retries and timeouts.

## S3 (`boac/externals/s3.py`)

| Use | Code | Bucket / key settings |
|---|---|---|
| Upload BOA attachments (notes, drafts, comments, templates) | `put_attachment_to_s3()` in `boac/lib/util.py` → `put_binary_data_to_s3()` | `DATA_LOCH_S3_ADVISING_NOTE_BUCKET`; key `DATA_LOCH_S3_BOA_NOTE_ATTACHMENTS_PATH/YYYY/MM/DD/YYYYMMDD_HHMMSS_{name}` |
| Download BOA attachments | `get_boa_attachment_stream()` (`boac/merged/advising_note.py`) | Same bucket; key is `path_to_attachment` |
| Download legacy SIS note and appointment attachments | `get_legacy_attachment_stream()` (`boac/lib/sis_advising.py`) | `DATA_LOCH_S3_ADVISING_NOTE_BUCKET`; key `DATA_LOCH_S3_ADVISING_NOTE_ATTACHMENT_PATH/{sid}/{filename}` |
| Download EOP attachments | `get_eop_attachment_stream()` | `DATA_LOCH_S3_EOP_ADVISING_NOTE_BUCKET`; key `DATA_LOCH_S3_EOP_NOTE_ATTACHMENTS_PATH/{note_id}_{display_name}` |
| Student photos | `_merge_photo_urls()` (`boac/merged/student.py`) | `DATA_LOCH_S3_PHOTO_BUCKET`; key `DATA_LOCH_S3_PHOTO_PATH/{uid}.jpg` |

- **Uploads** use `put_object` with `ServerSideEncryption=DATA_LOCH_S3_ENCRYPTION`. Upload errors are not caught.
- **Downloads** go through `stream_object()`, which opens the object with `smart_open` and returns a file-like stream. On any error it logs (with a clearer message for `NoSuchKey` / `AccessDenied`) and returns `None`. Legacy and EOP downloads check the loch first, so a missing row returns `None` without touching S3.
- **Photos** are presigned `get_object` URLs (`get_signed_urls()`), valid for `PHOTO_SIGNED_URL_EXPIRES_IN_SECONDS` (default 15 minutes). Signing doesn't check that the object exists, so a missing photo fails in the browser, not in BOA.

**Tests.** `fake_aws` starts moto's `mock_aws()` for the whole session, which also fakes STS. Buckets are created by `tests/util.py` helpers: `mock_advising_note_s3_bucket()` for uploads, and `mock_sis_note_attachment()`, `mock_legacy_appointment_attachment()`, and `mock_eop_note_attachment()`, which also put a known object. Since moto 5 the backend is shared, so `_ensure_bucket()` keeps them idempotent.

## SQS (`boac/externals/sqs.py`)

`send(table, operation, rows)` sends one message per row to `AWS_SQS_QUEUE_URL`. The body is JSON `{table, operation, row}`, where `row` is the model's `to_sqs_json()`. Each message gets a random `MessageDeduplicationId`. `MessageGroupId` is `row['note_id']` for `note_topics` and `row['id']` otherwise. If the queue URL is empty, `send()` returns without sending. A failed `send_message` is logged and skipped, but a failure building the client (STS) raises. `receive()` exists but has no callers. `sqs_status()` (for `/api/ping`) only builds a client and returns `False` on `ClientError`. Tables, operations, and callers are listed in `.claude/docs/notes-and-search.md`.

**Tests.** `fake_aws` creates a moto queue and overrides `AWS_SQS_QUEUE_URL` with its URL. Nothing consumes it, so tests seed the loch search tables directly.

## CAS and Google Analytics

- **CAS.** `_cas_client()` builds a `CASClientV3` with `server_url=CAS_SERVER` and a service URL pointing at `/cas/callback` (plus `?url=` for the post-login target). `/cas/callback` calls `verify_ticket(ticket)`. A UID that's missing, inactive, or disabled in BOA is redirected to `/` with an `error` param. Developer auth (`DEVELOPER_AUTH_ENABLED`, `DEVELOPER_AUTH_PASSWORD`) bypasses CAS and is what `fake_auth` uses.
- **Google Analytics** runs only in the browser. `initGoogleAnalytics()` configures vue-gtag when the user is logged in, not an admin, and `gaMeasurementId` is set. It sends the UID, department codes, and title as user properties.

## HTTP mocking (`boac/lib/mockingbird.py`)

`mockingbird` wraps the `responses` library for outgoing `requests` calls. `@mockable` passes a `mock` context manager into the function, `@mocking(func)` registers a fake `MockResponse`, and `@fixture('name_{arg}')` reads `FIXTURES_PATH/name_{arg}.json` (paged files `_page_N` get `Link: next` headers; a missing file gives 404). Setting `FIXTURE_OUTPUT_PATH` records real responses as fixtures. No current code uses these decorators. CalNet uses only its `_environment_supports_mocks()` and `_get_fixtures_path()` helpers. `boac/lib/http.py` keeps `sanitize_headers()` and `request()` (no timeout, returns a falsy `ResponseExceptionWrapper` on error) for HTTP clients, but nothing calls `request()` today.

## Gotchas

- **`demo` uses the fakes too.** `BOAC_ENV=demo` turns on `MockClient` and the CSV fixtures, not just `test`.
- **`None` from the loch means failure.** Check for it before iterating.
- **CSV fixtures shadow `loch.sql`.** In tests, `get_sis_section` and `get_sis_section_enrollments` never run SQL. Rows for those queries go in a CSV, not `loch.sql`.
- **CalNet misses are cached.** Bulk lookups and `force_feed=True` store a nearly empty feed, which stays until the key is cleared.
- **`skip_expired_users` isn't in the stow key.** The first caller decides whether expired people are included in `calnet_user_for_uid_{uid}`.
- **New loch schema settings need `loch.sql`.** Tests don't override `DATA_LOCH_*_SCHEMA`, so the fixture must create the schema under the default name.
- **Moto persists across tests.** Buckets and objects from earlier tests are still there.
- **CAS tests.** `test_cas_callback_with_invalid_ticket` pauses moto (`pause_mock_sts()`) and calls the unpatched `verify_ticket` against `CAS_SERVER`. Other CAS tests patch `verify_ticket`.
- **Never copy real data into fixtures.** CalNet, CSV, and loch fixtures must stay synthetic (`tests/CLAUDE.md`).
