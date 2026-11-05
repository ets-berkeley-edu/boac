# Admitted students (CE3)

Admitted students ("admits") are applicants admitted to UC Berkeley, served to the CE3 office (department code `ZCEEE`). Admit data is read-only. It comes from the Office of Undergraduate Admissions (OUA) tables in the data loch, and BOA stores nothing about admits except the SIDs in admit curated groups and the criteria of admit cohorts. The backend is `boac/api/admit_controller.py`, `boac/merged/admitted_student.py`, and the admit queries in `boac/externals/data_loch.py`. The frontend is `src/views/AdmitStudent.vue`, `src/views/AdmitStudents.vue`, and `src/components/admit/`.

Admit cohorts and their filters (`domain = 'admitted_students'`) are covered in `.claude/docs/cohorts.md`. Admit curated groups are covered in `.claude/docs/curated-groups.md`.

## Access

There are three checks, and they don't agree on peer advisors. See the "Two different CE3 checks" gotcha in `.claude/docs/permissions.md`.

| Check | Where | Rule |
|---|---|---|
| `@ce3_required` | `boac/api/decorators.py` → `can_access_admitted_students()` in `boac/api/util.py` | Admin, or an `advisor`/`director` membership in `ZCEEE` (`_is_advisor_in_department`). Also passes with a valid API key. Failure returns 401 |
| `is_unauthorized_domain(domain)` | `boac/api/util.py` | Blocks `'admitted_students'` unless admin or `ZCEEE` is in `dept_codes_where_advising()` (advisor/director). Callers return 403 or 404 |
| `canAccessAdmittedStudents` | `boac/merged/user_session.py` | Admin, or **any** `ZCEEE` membership. Same value as `canAccessPrivateNotes` |

Frontend:

- `src/lib/boa-user.ts` has no CE3 helper. Components read `currentUser.canAccessAdmittedStudents` (sidebar, search store, advanced search).
- The `/admit/student/:sid` and `/admit/students` routes (`src/router.ts`) use their own guard: admin, or `getDeptCodesPerRoles(currentUser, ['advisor', 'director']).includes('ZCEEE')` (`src/lib/berkeley-department.ts`). Anyone else is sent to `/404`. This matches `@ce3_required`, not the session flag.

## Data loch tables

The schema name is `DATA_LOCH_OUA_SCHEMA` (`boac_advising_oua` in `config/default.py`). The test loch defines both tables in `fixtures/loch/loch.sql`.

| Table | Used for |
|---|---|
| `student_admits` | One row per admit. `cs_empl_id` is the SID. In the test schema every column is `VARCHAR` except `created_at` / `updated_at`. Flags are compared as strings: `current_sir = 'Yes'`, `foster_care_flag = 'Y'`, `hispanic = 'T'`, `last_school_lcff_plus_flag = '1'`, `application_fee_waiver_flag = 'FeeWaiver'` (see `get_admitted_students_query`) |
| `student_admit_names` (`sid`, `name`) | Name-search index. In the fixtures it holds one uppercase row per name word. Search uppercases the phrase and uses `LIKE`, so stored names must be uppercase |
| `{student_schema}.student_profile_index` | Left-joined on `cs_empl_id = sid` to find a matching enrolled student (see below) |

## Backend

### Endpoints

| Method | Route | Decorator | What it does |
|---|---|---|---|
| GET | `/api/admit/by_sid/<sid>` | `@ce3_required` | Full admit record via `get_admitted_student_by_sid()`. 404 (`ResourceNotFoundError`) if not found |
| GET | `/api/admits/all?limit&offset&orderBy` | `@ce3_required` | Every admit, paged: `query_admitted_students()` with no filters. Returns `{sids, totalStudentCount, students}`. Defaults are 50 / 0 / `last_name` |
| POST | `/api/search/admits` `{searchPhrase, orderBy}` | `@ce3_required` (`boac/api/search_controller.py`) | Name or SID search via `search_for_admitted_students()`. 400 on an empty phrase. Returns `{admits, totalAdmitCount}` |

Admit data also flows through endpoints owned by other features:

- **Cohorts:** `CohortFilter.to_api_json()` → `_query_admitted_students()` (`boac/models/cohort_filter.py`) → `query_admitted_students()`.
- **Curated groups:** `boac/api/curated_group_controller.py` loads admit group members with `get_admitted_students_by_sids()`.
- **SID validation:** `POST /api/students/validate_sids` with `domain: 'admitted_students'` checks SIDs against `student_admits` (`boac/api/student_controller.py`).
- **CSV export:** `response_with_students_csv_download()` (`boac/api/csv_file_download_utils.py`) sends the admit domain to `_response_with_admits_csv_download()`, which is itself wrapped in `@ce3_required`. Rows come from `data_loch.get_admitted_students_by_sids()`, and the `cs_empl_id` column is aliased to `sid`. `POST /api/cohort_csv/download_per_filters` accepts an empty `filters` list for the admit domain; that's how "Export List" on `/admit/students` exports every admit.

### Query functions

| Function | File | Notes |
|---|---|---|
| `get_admitted_students_by_sids(offset, sids, limit, order_by)` | `data_loch.py` | Selects the full column list, with `cs_empl_id AS sid` and `s.uid AS student_uid` from the left join to `student_profile_index` |
| `get_admitted_student_by_sid(sid)` | `data_loch.py` | First row of the above |
| `get_admitted_students_query(...)` | `data_loch.py` | Builds `query_tables`, `query_filter`, and `query_bindings` for filters and name/SID search. The caller writes the `SELECT` |
| `get_admit_colleges()` and the other `get_admit_*()` | `data_loch.py` | Distinct non-blank values of one column, for cohort filter options |
| `query_admitted_students(...)` | `merged/admitted_student.py` | Runs a `SELECT DISTINCT(cs_empl_id)` for all matching SIDs, then (unless `sids_only`) a page of summary columns |
| `search_for_admitted_students(search_phrase, order_by)` | same | Runs the summary query and returns the first 50 rows plus the full count |
| `get_admitted_students_by_sids(sids, limit, offset, order_by)` | same | Wraps the loch function and validates `order_by` |
| `_to_api_json(admit)` | same | Camel-cases keys (`cs_empl_id` → `csEmplId`) and turns `updated_at` into an ISO `updatedAt` in UTC |

- `order_by` is checked against `ORDER_BY_OPTIONS_FOR_ADMITTED_STUDENTS` (`cs_empl_id`, `first_name`, `last_name`). Anything else falls back to `last_name`.
- **Search rules** (`get_admitted_students_query`): commas become spaces (in the controller). One all-digit word is a SID prefix match (`cs_empl_id LIKE '<digits>%'`). Otherwise the words are uppercased, de-duplicated, stripped of non-word characters, and each must prefix-match a `student_admit_names` row (one `JOIN` per word, capped at about ten words).

### Caching

- The admit endpoints and search aren't cached. Every request queries the loch.
- Cohort filter options are stowed in `json_cache` under `cohort_filter_options_admit_colleges`, `_admit_ethnicities`, `_admit_freshman_or_transfer`, `_admit_residency_categories`, and `_admit_special_program_cep` (`boac/lib/cohort_utils.py`). `load_filtered_cohort_counts()` (`boac/api/cache_utils.py`) clears `cohort_filter_options_%` during the current-term refresh.
- Admit cohorts store `sids` and `student_count` in `cohort_filters` like default cohorts, but they skip `track_membership_changes()`, so they have no `cohort_filter_events`.
- `update_curated_group_lists()` (`boac/api/cache_utils.py`) removes SIDs from admit curated groups when they're no longer in `student_admits`.

## Admits and enrolled students

- An admit and an enrolled student are the same person when `student_admits.cs_empl_id` equals `student_profile_index.sid`. The left join in `data_loch.get_admitted_students_by_sids()` returns that student's `uid` as `studentUid`, or `null` if there's no match (tested in `tests/test_merged/test_admitted_student.py`).
- `studentUid` is different from the admit's own `uid` column, which comes from OUA.
- The link is one-way. `AdmitStudent.vue` shows "View <name>'s profile page" (`studentRoutePath(admit.studentUid, currentUser.inDemoMode)`) when `studentUid` is set. The student profile page doesn't link back to the admit record.
- Admits and enrolled students never mix in one list. A curated group or cohort has one domain, and general search (`/api/search`) doesn't return admits.

## Frontend

| File | Role |
|---|---|
| `src/api/admit.ts` | `getAdmitBySid()` and `getAllAdmits(orderBy, limit, offset)`. Both track with `ga.student` |
| `src/api/search.ts` | `searchAdmittedStudents(phrase, orderBy = 'last_name')` |
| `src/views/AdmitStudent.vue` (`/admit/student/:sid`) | Profile page: name header, `ManageStudent` ("Add to Admission Group"), the link to the student page, `AdmitDataWarning`, and sections for academic, eligibility, demographic, family, contact, and GPA data |
| `src/views/AdmitStudents.vue` (`/admit/students`, sidebar "CE3 Cohorts") | Every admit, 50 per page with the page in `?p=`. Includes `SortBy domain="admitted_students"`, `CuratedGroupSelector`, `AdmitStudentsTable`, "Create Cohort" (`/cohort/new?domain=admitted_students`), and "Export List" behind `FerpaReminderModal` |
| `src/components/admit/AdmitStudentsTable.vue` | Plain `<table>` used by `AdmitStudents.vue`, `Cohort.vue`, and `CuratedGroup.vue`. Optional checkbox or remove-button column |
| `src/components/admit/SortableAdmits.vue` | `v-data-table-virtual` for search results, sorted on the client |
| `src/components/admit/AdmitDataWarning.vue` | Shows "Admit data was last updated on …" only when `updatedAt` is at least 24 hours old |
| `src/views/SearchResults.vue` | Runs `searchAdmittedStudents` when `?admits=true` and the phrase isn't blank. Renders the "admit" tab with `SortableAdmits` |
| `src/components/sidebar/Sidebar.vue` | "Admitted Students" section (CE3 cohorts and CE3 groups), shown when `canAccessAdmittedStudents` |

- **Sort preference.** `currentUser.preferences.admitSortBy` is separate from `sortBy`. `get_current_user_profile()` (`boac/api/util.py`) sets it to `last_name`, and `SortBy.vue` changes it in the store only (not saved on the server) and broadcasts `admitSortBy-user-preference-change`.
- **Demo mode.** Admit links put `window.btoa(sid)` in the URL, and `AdmitStudent.vue` decodes it with `atob`. Names, SIDs, birthdate, and contact fields get `demo-mode-blur`, and the page title becomes "Admitted Student".

**Accessibility patterns to keep (WCAG 2.2 AA):**

- Every cell in `AdmitStudentsTable` starts with `sr-only` context ("C S I D", "S I R", "U R E M", "First generation"). Empty values show an `aria-hidden` em dash plus `sr-only` "No data".
- `SortableAdmits` sets a caption with `v-table-caption`, spells out acronyms in header `ariaLabel`s, and announces sorting with `alertScreenReader`.
- After loading, focus goes to the page `h1` through `contextStore.loadingComplete('admit-name-header')` or `loadingComplete('cohort-name')`.
- `AdmitStudents.vue` has a "Skip to pagination" link (`sr-only sr-only-focusable`) and announces paging, sorting, and export cancel. Opening the FERPA dialog moves focus to `modal-header`.
- The remove button has `sr-only` "Remove <name>" and announces the removal. `AdmitDataWarning` uses `aria-live="polite"`.

## Tests

- `tests/test_api/test_admit_controller.py`: 401 for anonymous and non-CE3 users, and data for a CE3 advisor (`ce3_advisor_id`), for both admit endpoints.
- `tests/test_merged/test_admitted_student.py`: the merged shape, including `studentUid` with and without a matching student.
- Also `test_search_controller.py` (`test_search_admits_*`), `test_cohort_csv_controller.py` (admit-domain CSV), `test_externals/test_data_loch.py`, and the admit-domain cases in the cohort, curated group, and filter-option controller tests.
- Fixture admits are synthetic rows in `fixtures/loch/loch.sql`. Refer to them as `<sid>` in docs and comments.

## Gotchas

- **Two JSON shapes.** Queries built on `get_admitted_students_query` return `csEmplId`. Queries through `get_admitted_students_by_sids` return `sid` (plus `studentUid` and the full column list). Frontend code handles both with `student.csEmplId || student.sid` (`AdmitStudentsTable.getSid`, `CuratedStudentCheckbox`, `CuratedGroupSelector`).
- **Empty results are `None`.** `query_admitted_students` returns `students: None` and `search_for_admitted_students` returns `admits: None` when nothing matches, not `[]`.
- **Search returns at most 50.** `totalAdmitCount` is the full count, but `admits` is the first 50 in server order. `SortableAdmits` re-sorts only those rows.
- **Large limits are dropped.** `query_admitted_students` adds `LIMIT` only when `limit < 100`, so `limit=100` or more returns every row after `offset`.
- **`@ce3_required` on a helper.** `_response_with_admits_csv_download` is not a route, but it's decorated, so a non-CE3 user who reaches it gets a 401 from `login_manager.unauthorized()` rather than a CSV.
- **Status codes differ by path.** Admit endpoints return 401, `validate_sids` returns 403, `/api/cohort_csv/download_per_filters` returns 404, and `/api/cohort_csv/download` on a saved admit cohort returns 401 from the `@ce3_required` CSV helper (see `.claude/docs/csv-exports.md`).
- **Name search is prefix-only.** Each search word must match the start of a `student_admit_names` row (`LIKE 'WORD%'`). A fragment from the middle of a name finds nothing.
- **`AdmittedStudentResults.vue` isn't used.** `SearchResults.vue` renders the admit tab itself. Change the inline markup there.
- **Admit data is sensitive.** The profile and CSV include birthdate, home address, phone, income, citizenship, and ethnicity. Never copy fixture values into code, tests, or docs, and never log them.
