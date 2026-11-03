# Roles and permissions

BOA authorization has two parts. **Who you are** is an `authorized_users` row plus its department memberships. **What you can do** is a cached `UserSession` JSON blob that holds derived flags such as `isAdmin`, `canReadDegreeProgress`, and `canAccessAdmittedStudents`. Backend endpoints check that blob through the decorators in `boac/api/decorators.py`. The Vue router and components check the same blob through `src/lib/boa-user.ts` and `currentUser.*` flags.

## Data model

### `authorized_users` — `boac/models/authorized_user.py` (`AuthorizedUser`)

| Column | Meaning |
|--------|---------|
| `uid` | CalNet UID (unique) |
| `is_admin` | Superuser. Most checks short-circuit on it |
| `can_access_advising_data` | Notes/appointments data. Required by `advising_data_access_required` |
| `can_access_canvas_data` | bCourses/course-site data. Checked inline in `course_controller.get_section` and `search_controller` (courses domain) |
| `degree_progress_permission` | ENUM `generic_permission_types`: `'read'`, `'read_write'`, or NULL |
| `automate_degree_progress_permission` | If True, the nightly refresh may overwrite `degree_progress_permission` |
| `deleted_at` | Soft delete. `find_by_uid` and `get_id_per_uid` ignore deleted rows by default |
| `disabled_at` | Set by `disable_accounts_with_no_recent_activity()` (`boac/api/cache_utils.py`) after `LOGIN_INACTIVITY_THRESHOLD` days |
| `is_blocked` | Stops `create_or_restore()` from reviving a deleted user during the automated refresh |
| `in_demo_mode` | Blurs student personal data in the UI (`POST /api/user/demo_mode`) |

### Department roles — `boac/models/university_dept_member.py` (`UniversityDeptMember`)

- `university_dept_members(university_dept_id, authorized_user_id, role, automate_membership)`.
- `role` is the ENUM `university_dept_member_role_types`: `'advisor' | 'director'`. New memberships default to `'advisor'` (`create_or_update_membership`).
- Rows with `automate_membership=True` are deleted and rebuilt by `refresh_department_memberships()` (`boac/api/cache_utils.py`) from `data_loch.get_user_permissions_per_affiliations()`. `UniversityDept.delete_automated_members()` also soft-deletes any non-admin user left with no department or peer advising membership. Rows with `automate_membership=False` are managed by hand (admin UI, `POST /api/user/dept_membership/add`).
- There is **no "scheduler" role** any more. The `schedulers` table and `is_scheduler` column were dropped in `scripts/db/migrate/2024/20240122-BOAC-5013/`.

### Peer advising roles — `boac/models/peer_advising_department_member.py`

- `peer_advising_department_members(peer_advising_department_id, authorized_user_id, role_type, deleted_at)`, where `role_type` is `'peer_advisor' | 'peer_advisor_manager'`. Removing a member soft-deletes the row (`delete_membership`).
- Each `PeerAdvisingDepartment` belongs to a `university_dept`. In the session, peer advising memberships are merged into that university department's `memberships` list (`UserSession._get_api_json`).
- `_update_or_create_authorized_user()` (`boac/api/user_controller.py`) enforces these rules:
  - A peer advisor has exactly one department and no other role.
  - A peer advisor has no Canvas or advising data access.
  - A peer advisor manager must have `can_access_advising_data`.

### `authorized_user_extension.py`

`AuthorizedUserExtension` and `Advisor` are `__abstract__` and have no concrete subclass in `boac/` (unverified: looks like a leftover). Don't build new permission logic on them.

## Authentication

- **CAS:** `GET /cas/login_url` → CalNet → `GET|POST /cas/callback` (`auth_controller.cas_login`). The callback rejects the user if any of these hold:
  - `AuthorizedUser.get_id_per_uid(uid)` is None (unknown or deleted).
  - `UserSession.is_active` is False.
  - `is_disabled` is True.

  Otherwise it calls `login_user()` and `UserLogin.record_user_login(uid)`.
- **Dev auth:** `POST /api/auth/dev_auth_login` (`_dev_auth_login`). It works only when `DEVELOPER_AUTH_ENABLED` is set and the password matches `DEVELOPER_AUTH_PASSWORD`, and it applies the same active/disabled checks. When dev auth is off it returns 404.
- **Become user:** `POST /api/auth/become_user` (`@admin_required`) uses dev auth to switch users.
- **API key:** `_api_key_ok()` compares the `App-Key` request header with `config['API_KEY']` (default `None`, which disables it). API-key requests are also CSRF-exempt (`_enforce_csrf_protection` in `boac/routes.py`).
- **Session loader:** `boac/routes.py` registers `UserSession(user_id)` as both `user_loader` and `anonymous_user`. Unauthorized responses are JSON 401 (`unauthorized_handler`).

### `UserSession` — `boac/merged/user_session.py`

`load_user()` is cached with `@stow('boa_user_session_{user_id}')`. `_get_api_json()` builds the blob that `GET /api/profile/my` returns (`get_current_user_profile()` in `boac/api/util.py`). The frontend loads it in `src/main.ts` and stores it as `useContextStore().currentUser`. Key fields:

- `isActive` / `isAuthenticated`: these require a CalNet profile, and then either:
  - `is_admin`, or
  - at least one department whose roles are not just `['peer_advisor_manager']` (a manager also needs an advisor or director role).
- `isAdmin`, and `departments` (`[{deptCode, deptName, ..., memberships: [{role, automateMembership} | {role, peerAdvisingDepartmentId, peerAdvisingDepartmentName}]}]`).
- `canAccessAdvisingData`: the DB flag, but only if CalNet returns a `name`. `canAccessCanvasData`: the DB flag.
- `canAccessAdmittedStudents` and `canAccessPrivateNotes`: both equal `is_admin or 'ZCEEE' in departments`. This is the CE3 flag.
- `degreeProgressPermission`: forced to `'read_write'` for admins. `canEditDegreeProgress` means `read_write`. `canReadDegreeProgress` means `read` or `read_write`.
- `inDemoMode`, `disabledAt`, `deletedAt`, `isBlocked`, `uid`, `id`, plus CalNet profile fields. CalNet `departments` are renamed to `calNetDepartments`.

`get_current_user_profile()` adds `myCohorts`, `myCuratedGroups`, `myDraftNoteCount`, and `preferences`.

## Backend decorators (`boac/api/decorators.py`)

Every decorator also passes when `_api_key_ok()` is true, with exceptions noted under Gotchas. A failed check logs a warning and returns `login_manager.unauthorized()`, which is a **401**.

| Decorator | Allows | Example endpoint |
|-----------|--------|------------------|
| `admin_required` | `is_admin` | `GET /api/admin/cachejob`; `POST /api/user/dept_membership/add` |
| `admin_or_director_required` | admin, or `director` in any dept (`auth_utils.is_admin_or_director`) | `GET /api/reports/notes/<dept_code>` |
| `advisor_required` | admin, or `advisor`/`director` in any dept | `GET /api/cohorts/by_dept_code/<dept_code>` |
| `advising_data_access_required` | `can_access_advising_data` AND (admin, or advisor/director) | `POST /api/note/create_draft` |
| `director_advising_data_access_required` | `can_access_advising_data` AND (admin, or director) | `GET /api/notes/<sid>/download` |
| `advisor_or_peer_advisor_required` | admin, advisor/director, or `peer_advisor` | `POST /api/students/find_by_name_sid_or_email`; `POST /api/user/demo_mode` |
| `can_read_degree_progress` | `current_user.can_read_degree_progress` | `GET /api/degrees/student/<sid>` |
| `can_edit_degree_progress` | `current_user.can_edit_degree_progress` | `POST /api/degree/check/batch` |
| `ce3_required` | `util.can_access_admitted_students()`: admin, or **advisor/director** in `ZCEEE` | `GET /api/admit/by_sid/<sid>`; `POST /api/search/admits` |
| `peer_advisor_required` | admin or `peer_advisor` | `POST /api/peer_advising/note/create` |
| `peer_advisor_manager_required` | admin or `peer_advisor_manager` (any dept) | `DELETE /api/peer_advising/delete_peer_advisor/<dept_id>/<user_id>` |
| `peer_advisor_or_peer_advisor_manager` | admin, peer advisor, or peer advisor manager | `GET /api/peer_advising/note_topics` |
| `peer_advisor_manager_in_department` | admin, or a manager of the `peer_advising_department_id` from the URL or the POST body's `peerAdvisingDepartmentId` (`auth_utils.is_authorized_peer_advisor_manager`) | `GET /api/peer_advising/<peer_advising_department_id>/report/notes` |
| `peer_advisor_or_peer_advisor_manager_in_department` | admin, or a peer advisor/manager who is an active member of the department ID in the URL | `GET /api/peer_advising/<peer_advising_department_id>/notes` |
| `flask_login.login_required` | any authenticated session | `POST /api/auth/logout`; `GET /api/users/departments` |

Undecorated routes: `/cas/login_url`, `/cas/callback`, `/api/auth/dev_auth_login`, `/api/ping`, `/api/profile/my`, `/api/config`, `/api/version`, and `/api/service_announcement`.

## Department-scoped access (checked in the endpoint body, not by a decorator)

- `dept_codes_where_advising(departments)` (`boac/lib/berkeley.py`) returns the dept codes where the user is an advisor or director. This is the main scoping primitive.
- `get_student_query_scope()` (`boac/merged/student.py`) returns `['ADMIN']` for admins (and outside a request context), `[]` for anonymous users, and otherwise the user's advising dept codes. It drives which student data is surfaced, for example in `get_cohorts_by_dept_code`.
- **Admitted students (CE3):** `is_unauthorized_domain(domain)` (`boac/api/util.py`) blocks `'admitted_students'` unless the user is an admin or `ZCEEE` is in their advising dept codes. `@ce3_required` guards the admit endpoints.
- **Protected cohort filters:** `is_unauthorized_search()` limits the UWASC and COENG filter keys to members of those departments. See `.claude/docs/cohorts.md`.
- **Private notes:** note bodies and attachments are omitted unless `current_user.can_access_private_notes` (`boac/merged/advising_note.py`, `advising_search.py`). Toggling `isPrivate` requires the same flag (`notes_controller.py`). See `.claude/docs/notes-and-search.md`.
- **Creating advising notes:** `create_draft_note` raises 403 for admins and for users with no advising departments.
- **Director of a specific dept:** `_current_user_is_director_of(dept_code)` (`admin_reports_controller.py`).
- **Degree templates tied to a student:** archiving and unarchiving them needs `is_admin_or_director` (`degree_progress_controller.py`).
- **COENG-only permissions:** `degree_progress_permission` is only kept for users in `COENG` (`_update_or_create_authorized_user`). COE CSV columns depend on `'COENG' in dept_codes_where_advising` (`csv_file_download_utils.py`).
- **Peer advising:**
  - Note creation checks that the user is a member of the posted `peerAdvisingDepartmentId` (`create_peer_advising_note`).
  - `GET /api/peer_advisor/<uid>/notes` is restricted to that user or an admin.
  - Manager actions on a specific peer advisor call `is_authorized_peer_advisor_manager(..., peer_advisor_user_id=...)` inline, which also stops a manager from acting on themselves.

## Frontend counterparts

`src/lib/boa-user.ts` (all built on `getUserDepartmentsWithRoles` in `src/lib/berkeley-department.ts`):

| Helper | Logic | Backend analogue |
|--------|-------|------------------|
| `isAdvisor(user)` | `advisor` role anywhere | part of `advisor_required` |
| `isDirector(user)` | `director` role anywhere | `admin_or_director_required` (without the admin part) |
| `isCoe(user)` | advisor/director in `COENG` | inline `'COENG' in dept_codes_where_advising` (no decorator) |
| `isPeerAdvisor(user)` | `peer_advisor` role | `peer_advisor_required` |
| `isPeerAdvisorManager(user)` | `peer_advisor_manager` role | `peer_advisor_manager_required` |

Router guards (`beforeEnter` in `src/router.ts`) send unauthenticated users to login and authenticated-but-unauthorized users to `/404`:

- `StandardLayout` routes (`/cohort/:id`, `/student/:uid`, `/search`, ...): `isAdvisor || isDirector || isAdmin`, matching `advisor_required`.
- `/peer/management/:id`: admin, or `getPeerAdvisorDepartmentMemberships(user, 'peer_advisor_manager')` contains `:id`, matching `peer_advisor_manager_in_department`.
- `/peer_advisor/*` (`PeerAdvisor` layout): `isAdmin || isPeerAdvisor`, matching `peer_advisor_required`.
- `/admin`, `/admin/passengers`: `isAdmin`, matching `admin_required`.
- `/analytics/:deptCode`: `isDirector || isAdmin`, matching `admin_or_director_required`.
- `/admit/students`, `/admit/student/:sid`: admin, or `getDeptCodesPerRoles(user, ['advisor','director']).includes('ZCEEE')`, matching `ce3_required`.
- Degree routes (`/degrees`, `/degree/:id`, ...): `$_requiresDegreeProgress` checks `currentUser.canReadDegreeProgress`, matching `can_read_degree_progress`.
- `/home`, `/profile`, and `/404`: peer advisors are redirected to `/peer_advisor${path}`.

Component-level flags:

- `currentUser.canAccessCanvasData`: `StudentRowCourseActivity.vue`, `stores/search.ts`.
- `canAccessAdmittedStudents`: `Sidebar.vue`.
- `canAccessPrivateNotes`: `EditAdvisingNote.vue`, `EditBatchNoteModal.vue`.
- `isPeerAdvisorManager`: `PeerAdvisingNotesTable.vue`.

## Tests: logging in as a role

- The `fake_auth` fixture (`tests/conftest.py`): `FakeAuth.login(uid)` posts to `/api/auth/dev_auth_login` with `DEVELOPER_AUTH_ENABLED` overridden to True. To test anonymous access, skip `login`. For API keys, use `override_config(app, 'API_KEY', ...)` plus the header (see `tests/test_api/test_cachejob_controller.py`).
- Users come from `fixtures/development_db/test_users.json`. Memberships come from `university_depts.json` and `peer_advising_departments.json`. They're loaded by `boac/models/development_db.py`, which also writes a mock CalNet entry (`calnet_user_for_uid_{uid}`) into `json_cache`. A user needs that CalNet entry to count as active.
- These fixtures are synthetic. Refer to test users only by UID, never by name.
- Test files declare module-level constants such as `admin_uid = '2040'` and `coe_advisor_uid = '1133399'`.

| UID | Role(s) (from fixtures) |
|-----|------------------------|
| `2040`, `177473`, `95509`, `1049291` | admin |
| `44444` / `33333` | deleted admin / deleted user (`development_db.py`) |
| `1015674`, `666`, `1024` | deleted (`"deleted": true`); used as `unauthorized_uid` |
| `1081940` | UWASC advisor (manual) |
| `6446` | UWASC director |
| `90412` | COENG advisor (automated) + UWASC director |
| `1133399` | COENG advisor, degree `read_write`, + peer advisor manager (Mechanical Engineering, COENG) |
| `6972201` | COENG advisor, degree `read`, no Canvas |
| `9933311` | COENG director, degree `read_write` |
| `211159` | COENG advisor, degree `read_write` |
| `1022796` | COENG advisor + QCADV director, `can_access_advising_data=False` |
| `53791` / `222719` | QCADV (+QCADVMAJ) director / QCADV director |
| `188242`, `19735` | QCADV advisor (`19735` has no advising data) |
| `242881`, `1133397` | QCADVMAJ advisor (automated) |
| `2525`, `3535` | ZCEEE advisor + peer advisor manager (NAVCAL / EOP); CE3 |
| `5405613` | ZCEEE advisor (CE3) |
| `1563405`, `1133400`, `188444`, `1913062` | peer advisors (EOP, NAVCAL, NAVCAL, Mechanical Engineering) |

## Adding a new endpoint

1. Choose the narrowest decorator from the table. Use `advising_data_access_required` whenever notes or appointments are returned.
2. If access depends on a specific department or resource, add an inline check (`dept_codes_where_advising`, `get_student_query_scope`, `is_authorized_peer_advisor_manager`, or an ownership check) and `raise ForbiddenRequestError` (403).
3. For admitted-student data, use `@ce3_required` and/or `is_unauthorized_domain`.
4. Mirror the check in the frontend: a router guard in `src/router.ts`, or a `currentUser.*` / `boa-user.ts` check in the component. The frontend check only hides UI; the backend check is what enforces access.
5. If the endpoint changes a user's permissions, call `UserSession.flush_cached_user_session(user_id)`.
6. In `tests/test_api/`, test anonymous access (401), each denied role (401/403), and each allowed role, using UIDs from the table above.

## Gotchas

- **The API key doesn't work alone on peer decorators.** In `advisor_or_peer_advisor_required` and the five `peer_advisor*` decorators, `_api_key_ok()` sits *inside* `current_user.is_authenticated and (...)`, so a request with only the key gets 401.
- **401 vs 403.** Decorators return **401**; inline checks usually raise `ForbiddenRequestError` (**403**, `boac/api/error_handlers.py`). Tests assert specific codes.
- **The session is cached.** `UserSession.load_user` uses `@stow`, so DB changes to roles or flags are invisible until the cache is flushed (`flush_cached_user_session`, or a login with `flush_cached=True`).
- **Two different CE3 checks.** The session's `canAccessAdmittedStudents` / `canAccessPrivateNotes` are true for *any* ZCEEE membership, including merged-in peer advising memberships. `ce3_required` and `is_unauthorized_domain` require an advisor or director role in ZCEEE. So a ZCEEE peer advisor may see a true flag in the UI but get 401/403 from the API (unverified whether this is intended).
- **`can_access_admitted_students(user)`** (`boac/api/util.py`) reads `current_user` for the role check, not its argument.
- **Admins are not "advisors".** `create_draft_note` rejects admins, and `isAdvisor()` is false for an admin with no departments.
- **`advisor_required` doesn't check `is_authenticated`.** It relies on the anonymous `UserSession` having no departments.
- **A manager role alone doesn't count.** A user whose only role is `peer_advisor_manager` is inactive and cannot log in (`_get_api_json`).
- **Automated memberships are rebuilt nightly.** `automate_membership=True` rows are deleted and recreated, and users left with no membership are soft-deleted unless they're admins. To keep a manual grant, set `automate_membership=False`. To keep a removed user from coming back, set `is_blocked`.
- **Missing CalNet data revokes access.** Without a CalNet profile a user is inactive, and without a CalNet name `canAccessAdvisingData` is False, even when the DB flags say otherwise.
- **`UserSession.same_day_advisor_departments`** reads `sameDayAdvisorStatus`, which `_get_api_json` never sets, so accessing it raises `KeyError`. It's dead code; don't use it.
