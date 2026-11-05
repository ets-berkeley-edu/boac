# Users and admin tools

BOA admins manage who can use BOA in the **Passenger Manifest** (`/admin/passengers`), edit the service announcement and topics on the **Flight Deck** (`/admin`), and read usage reports in the **Flight Data Recorder** (`/analytics/:deptCode`, admins and directors). Every user sees their own settings on **Profile** (`/profile`). Key files: `boac/api/user_controller.py`, `boac/api/admin_reports_controller.py`, `boac/api/config_controller.py`, `boac/models/authorized_user.py`, `boac/models/university_dept.py`, `boac/models/university_dept_member.py`, and `boac/merged/advising_notes_reports.py`.

Related docs (not repeated here):

- `.claude/docs/permissions.md`: the `authorized_users` columns, department and peer roles, the `UserSession` blob, decorators, CAS/dev-auth/become-user login, and router guards.
- `.claude/docs/peer-advising.md`: managers adding and removing peer advisors, and `POST /api/users/peer_advising`.
- `.claude/docs/notes-and-search.md`: topics (the Flight Deck's "Manage Topics" uses `boac/api/topic_controller.py`).

## Data touched by admin tools

| Table / model | Notes |
|---|---|
| `authorized_users` (`AuthorizedUser`) | Columns are listed in permissions.md. A new row gets `can_access_advising_data` and `can_access_canvas_data` True by default (`AuthorizedUser.__init__`). `created_by` is the creating admin's UID, or `'0'` for the automated refresh. |
| `university_depts` (`UniversityDept`) | `dept_code`, `dept_name`. No API creates them. `get_all_departments()` returns `memberCount` and, optionally, `peerAdvisingDepartments`. |
| `university_dept_members` (`UniversityDeptMember`) | PK `(university_dept_id, authorized_user_id)`, so one row (one role) per user per department. Removing a membership **hard-deletes** the row (`delete_membership`). |
| `user_logins` (`UserLogin`) | One row per login. `last_login(uid)` feeds `lastLogin` in user lists and the inactivity check. |
| `tool_settings` (`ToolSetting`) | Key/value strings. Holds `SERVICE_ANNOUNCEMENT_TEXT` and `SERVICE_ANNOUNCEMENT_IS_PUBLISHED`. `upsert()` stores `str(value)`. |

## Creating and editing a user

`POST /api/user/create_or_update` (`create_or_update_user_profile`) takes the whole user object from the edit modal: `{user: {id?, uid, isAdmin, isBlocked, isDisabled, canAccessAdvisingData, canAccessCanvasData, degreeProgressPermission, automateDegreeProgressPermission, deletedAt, departments: [{deptCode, memberships: [{role, automateMembership, peerAdvisingDepartmentId?}]}]}}`. It runs these steps:

1. `_update_or_create_authorized_user()`:
   - Drops `degreeProgressPermission` and `automateDegreeProgressPermission` unless `COENG` is among the departments.
   - Applies the peer advisor and manager rules (400 on violation; see permissions.md).
   - If `isDisabled` is False, calls `UserLogin.record_user_login(uid)` so the inactivity job doesn't disable the account again right away.
   - **Update** (`id` present): `AuthorizedUser.update_user(...)` overwrites every flag with the posted values.
   - **Create** (no `id`): 400 if the UID already exists, even as a deleted row. The UID must resolve in CalNet with a `csid` (`get_calnet_user_for_uid(..., skip_expired_users=True)`), otherwise 400 "Invalid UID". Then `AuthorizedUser.create_or_restore(..., created_by=current_user.uid)`.
2. **Delete or restore.** A truthy `deletedAt` soft-deletes (`AuthorizedUser.delete`); an empty one on a deleted row restores it (`un_delete`). There is no hard delete.
3. **Memberships are replaced, not merged.** `_delete_existing_memberships()` removes every university membership and soft-deletes every peer membership. `_update_or_create_department_memberships()` then recreates them from `departments`. Advisor and director roles go to `UniversityDeptMember.create_or_update_membership`. Peer roles go to `PeerAdvisingDepartmentMember.create_or_update_membership`, and they stay soft-deleted if the user is deleted.
4. Flushes the session cache and returns `authorized_users_api_feed([user])[0]`.

### `create_or_restore` semantics (`boac/models/authorized_user.py`)

- If the existing row is `is_blocked` and the caller passes no `is_blocked`, it returns `False` and changes nothing. This is how a blocked user stays out during the automated refresh.
- On a **deleted** row it overwrites the flags with the passed values. On a **live** row it only upgrades flags (False → True), but always sets `degree_progress_permission` and `created_by`.
- `is_disabled=True` / `False` sets or clears `disabled_at`; `None` leaves it alone.

### Status filters (`_users_sql_where_clause`, `get_admin_users`)

| `status` | Matches |
|---|---|
| `active` | `deleted_at IS NULL AND disabled_at IS NULL` (admins: also not blocked) |
| `deleted` / `disabled` / `blocked` | `deleted_at` set / `disabled_at` set / `is_blocked` |
| none | everyone |

## Endpoints

| Method | Route | Decorator | What it does |
|---|---|---|---|
| GET | `/api/profile/my` | none | Current session blob plus `myCohorts`, `myCuratedGroups`, `myDraftNoteCount`, `preferences` (`get_current_user_profile`) |
| GET | `/api/user/session_keep_alive` | `login_required` | Returns the session JSON. The frontend pings it every `pingFrequency` ms |
| GET | `/api/user/calnet_profile/by_csid/<csid>`, `.../by_uid/<uid>`, `.../by_user_id/<user_id>` | `advisor_required` | CalNet lookups. `by_user_id` includes deleted users and returns 404 if there is no row |
| GET | `/api/user/by_uid/<uid>?includeDeleted=` | `advisor_required` | One user feed entry, 404 if missing. `includeDeleted` is honored only for admins |
| POST | `/api/users` `{deptCode, role, status, sortBy, sortDescending, isCsvDownloadRequest}` | `admin_required` | Filtered user list (`AuthorizedUser.get_users`), or a `boa-users` CSV |
| POST | `/api/users/admins` `{status, sortBy, sortDescending, isCsvDownloadRequest}` | `admin_required` | Admin users by status, or a `boa-admin-users` CSV |
| POST | `/api/users/autocomplete` `{snippet}` | `admin_required` | Digits: UID prefix match. Otherwise: CalNet name match against every UID in `authorized_users`. Returns `[{name: 'Name (uid)', uid}]` |
| POST | `/api/user/create_or_update` `{user}` | `admin_required` | See above |
| POST | `/api/user/dept_membership/add` `{uid, deptCode, role, automateMembership}` | `admin_required` | `create_or_update_membership`; `automateMembership` defaults to True |
| POST | `/api/user/dept_membership/update` | `admin_required` | `update_membership`; null fields are left unchanged; 400 if no such membership |
| DELETE | `/api/user/dept_membership/delete/<university_dept_id>/<authorized_user_id>` | `admin_required` | Hard-deletes the membership; 404 if missing |
| POST | `/api/user/demo_mode` `{demoMode}` | `advisor_or_peer_advisor_required` | Sets `in_demo_mode` and re-logs the user in. 404 unless `DEMO_MODE_AVAILABLE` |
| GET | `/api/users/departments` | `login_required` | `get_all_departments(include_peer_advising_departments=True)`, with "Other" moved last |
| GET | `/api/config` | none | Frontend bootstrap (below) |
| GET | `/api/version` | none | `boac.__version__` plus `config/build-summary.json` if present |
| GET | `/api/service_announcement` | none | `null` when anonymous. Non-admins get it only when published; admins always get `{text, isPublished}` |
| POST | `/api/service_announcement/update` `{text}` | `admin_required` | Runs `process_input_from_rich_text_editor`. 400 if empty while published |
| POST | `/api/service_announcement/publish` `{publish}` | `admin_required` | Stores the published flag; 400 if `publish` is missing |
| GET | `/api/reports/available_departments` | `admin_or_director_required` | Admins: every dept code with members. Directors: their director depts |
| GET | `/api/reports/notes/<dept_code>` | `admin_or_director_required` + `_current_user_is_director_of` (403) | Note counts (BOA, SIS, ASC, E&I, peer advising). 404 for a code not in `BERKELEY_DEPT_CODE_TO_NAME` |
| GET | `/api/reports/users/<dept_code>` | same | That department's users (any status) with `notesCreated` (`get_note_count_per_user`) |
| GET | `/api/reports/boa_notes/monthly_count` | `admin_or_director_required` | Year → month → department note counts, split into advisor and peer notes |
| GET | `/api/reports/boa_notes/metadata` | `admin_required` | CSV of every BOA note's metadata plus student name, degrees, cohorts, and curated groups (`get_summary_of_boa_notes`) |
| GET | `/api/reports/low_assignment_scores?term=` | `admin_required` | Canvas low-score analysis for a term (`low_assignment_scores`). No frontend caller |

Become-user (`POST /api/auth/become_user`) and the cache job (`/api/admin/cachejob/*`) are covered in permissions.md and alerts.md.

## Session cache after a change

`UserSession.flush_cached_user_session(user_id)` (`boac/merged/user_session.py`) clears the `json_cache` key `boa_user_session_{user_id}`. The next request for that user rebuilds the blob from the DB and CalNet. These paths flush:

- `create_or_update_user_profile` (after `update_user`, after rebuilding memberships, and at the end).
- `set_demo_mode` (`current_user.flush_cached()`, then `login_user(UserSession(..., flush_cached=True))`).
- Login and logout in `boac/api/auth_controller.py`.

Any new code that changes a user's flags or memberships must call `flush_cached_user_session` for that user.

## Automated changes

`load_term()` (`boac/api/cache_utils.py`), for the current term only, runs `refresh_department_memberships()` and then `disable_accounts_with_no_recent_activity()`. The first rebuilds `automate_membership=True` rows from the data loch (see permissions.md). The second sets `disabled_at` on users with no login, or no account creation if they never logged in, within `LOGIN_INACTIVITY_THRESHOLD` days (default 365, `config/default.py`).

## Config bootstrap (`GET /api/config`)

`src/main.ts` calls `/api/config` before anything else and stores the result with `contextStore.setConfig({...data, apiBaseUrl, isVueAppDebugMode})`. Then it loads `/api/profile/my` → `setCurrentUser` (which also loads `/api/users/departments`) → the service announcement → the keep-alive interval → mounts the router.

- The payload holds term IDs, attachment rules, note contact types (with `isAvailableToPeerAdvisors`), degree-progress options, feature flags (`devAuthEnabled`, `isDemoModeAvailable`), `fixedWarningOnAllPages`, `pingFrequency`, `timezone`, and `csrfToken`.
- `csrfToken` is sent as a header on POST/PUT/PATCH/DELETE by the interceptor in `src/lib/axios-utils.ts`.
- The endpoint is anonymous. Only expose values that are safe for anyone to see.
- To add a value: set a default in `config/default.py`, add it to `app_config()`, and add it to `BoaConfig` in `src/lib/types.ts`. The Flight Deck lists every config key.

## Frontend

| File | Role |
|---|---|
| `src/api/user.ts` | `getUsers`, `getAdminUsers`, `getPeerAdvisingUsers` (each one downloads a CSV when given a filename prefix), `getUserByUid`, `userAutocomplete`, `createOrUpdateUser`, `becomeUser`, `setDemoMode`, `getDepartments`, `getUserProfile`, `getCalnetProfileBy*`. The `dept_membership/*` endpoints have no client |
| `src/api/admin-reports.ts` | `getAvailableDepartmentReports`, `getNotesReport`, `getUsersReport`, `getBoaNoteCountByMonth` |
| `src/api/config.ts` | `getVersion`, `getServiceAnnouncement`, `updateAnnouncement`, `publishAnnouncement` (both update `contextStore.announcement`) |
| `src/views/PassengerManifest.vue` + `src/stores/manifest.ts` | "Search" mode (autocomplete → `getUserByUid`) or "Filter" mode (role, department, status). Filtering by a peer role calls `getPeerAdvisingUsers`, `admin` calls `getAdminUsers`, and anything else calls `getUsers`. The CSV button downloads all active users |
| `components/admin/passenger-manifest/` | `BoaUsers.vue` (table, expandable raw JSON row, "become" button shown only when `config.devAuthEnabled`), `EditUser.vue` (the modal), `ManageBoaUserPermissions.vue`, `ManageBoaUserDepartments.vue`, `SelectBerkeleyDepartment.vue` (up to three departments), `ManageDegreeProgressPermission.vue` (shown for COE users or users who already have a permission), `QuickLinks.vue` (CE3, COE, QCADV, peer roles) |
| `src/views/FlightDeck.vue` | Version and git commit, `DemoModeToggle`, `EditServiceAnnouncement`, `ManageTopics`, and a table of every config key |
| `src/views/FlightDataRecorder.vue` | Department picker from `available_departments` (default `QCADV`), `components/reports/NotesReport.vue`, `UserReport.vue` |
| `src/views/Profile.vue` | `MyProfile.vue` (name, UID, SIS ID, email, degree-progress permission, roles) and `DemoModeToggle` when demo mode is available. Also used at `/peer_advisor/profile` |
| `src/layouts/shared/ServiceAnnouncement.vue` | Banner in `StandardLayout` and `PeerAdvisor` layouts; dismiss/restore state lives only in the Pinia store (`contextStore.dismissedServiceAnnouncement`), so it resets on reload |

`HeaderMenu.vue` links to these pages. Admins open the analytics page at `/analytics/qcadv`, and directors open it at their director department.

**Accessibility patterns to keep:**

- Modals use `ModalHeader`, `aria-labelledby="modal-header"`, and `toggleModalBackgroundDisabled`. On close, focus returns to `edit-<uid>` or `add-new-user-btn` (`putFocusNextTick`), and cancel is announced with `alertScreenReader`.
- `EditUser.vue` shows save errors in a `role="alert"` region. The Save button stays disabled until every department has a role, and every peer role has a peer department.
- Each filter `<select>` has an `aria-label`. Changing one moves focus to the next control (watchers in `SearchAndFilterBoaUsers.vue`).
- `BoaUsers.vue` has a table caption (`v-table-caption`), `SortableTableHeader`, sort announcements, an `sr-only` "Showing N users", and icon buttons with `aria-label` ("Edit profile of …", "Log in as …"). External and mailto links say "(opens in new tab)".
- The service banner is an `aria-live="assertive"` alert. The dismiss and restore buttons move focus to each other, and the restore button is `sr-only`. Publishing and updating are announced.
- `DemoModeToggle.vue` is a native checkbox with a `<label>` and `aria-describedby`, and focus returns to it after the save. Name fields get `demo-mode-blur` in demo mode.
- `NotesReport.vue` uses `aria-expanded` on the show/hide button, a `role="status"` loading message, and tables with captions.

## Tests

`tests/test_api/test_user_controller.py` (profile, CalNet lookups, dept membership CRUD, filters, admins, autocomplete, demo mode, CSV, create/update, and peer role rules), `test_admin_reports_controller.py`, `test_config_controller.py`, and `test_cachejob_controller.py`. Use the module-level UID constants already in those files; don't add real UIDs.

## Gotchas

- **Send the full department list.** `create_or_update` rebuilds all memberships from the payload, so a partial `departments` list removes the rest.
- **The Admin checkbox is disabled when the user has departments** (`ManageBoaUserPermissions.vue`). The backend doesn't enforce this.
- **Degree-progress fields are silently dropped** unless `COENG` is in the posted departments.
- **Users without CalNet data vanish from lists.** `authorized_users_api_feed` (`boac/api/util.py`) skips any user whose CalNet lookup is empty, and it reports `canAccessAdvisingData` False when CalNet has no name.
- **Notes report counts are campus-wide.** `get_notes_report_by_dept` uses `dept_code` only to authorize. The count helpers it calls are invoked without a department.
- **Autocomplete by name is heavy.** A non-numeric snippet loads CalNet records for every row in `authorized_users`, including deleted users.
- **Tool settings are strings.** `SERVICE_ANNOUNCEMENT_IS_PUBLISHED` is stored as `'True'`/`'False'` and read back with `to_bool_or_none`.
- **The report CSV holds student data.** `/api/reports/boa_notes/metadata` includes SIDs and names. Keep it `admin_required`, and never log or fixture its rows.
