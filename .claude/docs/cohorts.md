# Cohorts and cohort filters

A cohort is a set of students matching one or more filter criteria, which BOA dynamically fetches from the data loch. Users can define their own cohorts containing one or more filters and query for matching students. Saved cohorts are stored in the `cohort_filters` database table. Component filters of cohorts are serialized as a JSON object in the `filter_criteria` column.

## Domains

Cohorts have a `domain` field (either `'default'` or `'admitted_students'`) that determines which student population is searched and which filters are available:

- **`default`** — active enrolled students. Available to all authenticated users.
- **`admitted_students`** — prospective students who have been admitted but not yet enrolled. Available only to admins and users in the ZCEEE department.

The domain also controls which query path runs in `CohortFilter.to_api_json()`: either `_query_students()` (joins against SIS/enrollment data) or `_query_admitted_students()` (joins against admit data).

## Database schema

```sql
cohort_filters (
  id              INTEGER PRIMARY KEY,
  domain          VARCHAR,           -- 'default' or 'admitted_students'
  owner_id        INTEGER REFERENCES authorized_users,
  name            VARCHAR(255),
  filter_criteria JSONB,             -- stored filter selections
  sids            TEXT[],            -- cached SID list (deferred column)
  student_count   INTEGER,           -- cached count
  alert_count     INTEGER,           -- cached alert count
  created_at      TIMESTAMP,
  updated_at      TIMESTAMP
)

cohort_filter_events (
  id               INTEGER PRIMARY KEY,
  cohort_filter_id INTEGER REFERENCES cohort_filters,
  sid              VARCHAR(80),
  event_type       ENUM('added', 'removed'),
  created_at       TIMESTAMP
)
```

The `sids` column is a deferred SQLAlchemy column — it is not loaded unless explicitly accessed — to avoid expensive array deserialization in list contexts. `cohort_filter_events` is an audit trail; every time a cohort's membership changes (student added or removed), a row is written.

## Filter criteria storage format

Filters are stored in the `filter_criteria` JSONB column as a dictionary mapping filter keys to arrays of selected values:

```json
{
  "gpaRanges": [{"min": 2.0, "max": 3.5}],
  "majors": ["Computer Science", "Mathematics"],
  "academicCareers": ["undergraduate"],
  "groupCodes": ["MFB-DB"],
  "coeAdvisorLdapUids": ["uid123"],
  "transfer": true,
  "curatedGroupIds": [1, 2, 3]
}
```

Each key corresponds to a filter definition in `CohortFilterOptions`. Values may be strings, booleans, or range objects depending on the filter's `type.db` field (`'string[]'`, `'boolean'`, `'json[]'`).

The UI representation is a flat array of `{key, value}` pairs, one per selection:

```json
[
  {"key": "majors", "value": "Computer Science"},
  {"key": "majors", "value": "Mathematics"},
  {"key": "gpaRanges", "value": {"min": 2.0, "max": 3.5}}
]
```

Translation between the two representations happens in `boac/api/util.py`:
- `translate_filters_to_cohort_criteria(filters, domain)` — UI array → JSONB dict
- `get_cohort_filter_db_type_per_key(domain)` — returns the `type.db` for each filter key

## Filter catalog

All available filters are defined in `boac/merged/cohort_filter_options.py` (`CohortFilterOptions`). Each filter definition includes:

```python
{
  'key': 'majors',
  'label': {
    'primary': 'Major',
    'range': None,
    'rangeMinEqualsMax': ''
  },
  'options': [{'name': 'Computer Science', 'value': 'COMPSCI'}, ...],
  'type': {
    'db': 'string[]',   # storage type: 'string[]', 'boolean', 'json[]'
    'ux': 'options'     # UI widget: 'options', 'option_groups', 'range', 'boolean'
  },
  'availableTo': '*',   # '*' or list of dept codes e.g. ['COENG', 'UWASC']
  'domain': 'default',
  'disabled': False
}
```

### Filter categories (default domain)

**Academic**
`academicCareers`, `academicDivisions`, `academicStandings`, `academicCareerStatus`, `colleges`, `degrees`, `degreeTerms`, `enteringTerms`, `expectedGradTerms`, `gpaRanges`, `lastTermGpaRanges`, `incomplete`, `incompleteDateRanges`, `intendedMajors`, `levels`, `majors`, `midpointDeficient`, `minors`, `graduatePrograms`, `studentHolds`, `transfer`, `unitRanges`, `visaTypes`

**Advising**
`cohortOwnerAcademicPlans` (My Students), `curatedGroupIds` (My Curated Groups), `epnCpnGradingTerms`

**Demographics**
`ethnicities`, `underrepresented`

**Departmental — ASC** (restricted to UWASC members)
`groupCodes`, `inIntensiveCohort`, `isInactiveAsc`

**Departmental — COE** (restricted to COENG members)
`coeAdvisorLdapUids`, `coeAcademicStandings`, `coeEthnicities`, `coePrepStatuses`, `coeUnderrepresented`, `isInactiveCoe`

### Filter categories (admitted_students domain)

`admitColleges`, `familyDependentRanges`, `freshmanOrTransfer`, `hasFeeWaiver`, `inFosterCare`, `isFamilySingleParent`, `isFirstGenerationCollege`, `isHispanic`, `isLastSchoolLCFF`, `isReentry`, `isSir`, `isStudentSingleParent`, `isUrem`, `residencyCategories`, `specialProgramCep`, `studentDependentRanges`, `xEthnicities`

### Protected filters and access control

Two sets of filters are department-restricted:

```python
PROTECTED_COHORT_FILTERS_UWASC = ['groupCodes', 'inIntensiveCohort', 'isInactiveAsc']
PROTECTED_COHORT_FILTERS_COENG = ['coeAcademicStandings', 'coeAdvisorLdapUids',
                                   'coeEthnicities', 'coePrepStatuses',
                                   'coeUnderrepresented', 'isInactiveCoe']
```

`is_unauthorized_search(filter_keys, order_by)` in `boac/api/util.py` enforces this at the API layer: non-members who try to search with protected filter keys (or sort by `group_name`, which is ASC-only) receive a 403.

## Backend layers

### Model — `boac/models/cohort_filter.py`

`CohortFilter` is the SQLAlchemy ORM model. Key methods:

| Method | Purpose |
|--------|---------|
| `create(uid, name, filter_criteria, domain)` | Inserts a new cohort row |
| `update(cohort_id, name, filter_criteria, alert_count)` | Updates name or criteria |
| `delete(cohort_id)` | Removes cohort and events |
| `find_by_id(cohort_id)` | Single-cohort lookup |
| `get_cohorts(user_id)` | All cohorts for a user |
| `get_cohorts_owned_by_uids()` | Multi-user lookup (used by dept advisors) |
| `to_api_json(order_by, offset, limit, ...)` | Full response with paginated students |
| `to_base_json()` | Lightweight response without student data |
| `clear_sids_and_student_count()` | Invalidates cached SIDs/count |
| `update_sids_and_student_count(sids, count)` | Refreshes cache after search |
| `update_alert_count(count)` | Refreshes alert cache |
| `track_membership_changes()` | Diffs old vs new SIDs, writes CohortFilterEvent rows |
| `refresh_alert_counts_for_owner(owner_id)` | Batch-updates alert counts for a user |

### Merged layer — `boac/merged/cohort_filter_options.py`

`CohortFilterOptions` is the bridge between stored criteria and the filter UI. Key methods:

| Method | Purpose |
|--------|---------|
| `get_all_filter_categories()` | Full filter catalog, organized by category |
| `get_filter_categories_per_domain(domain)` | Domain-scoped and permission-scoped catalog |
| `get_customized_filter_categories(domain, owner_uid, existing_filters)` | Catalog with already-selected options marked disabled |
| `translate_to_filter_options(owner_uid, domain, criteria)` | JSONB dict → UI `[{key, value, label}, ...]` array |
| `populate_cohort_filter_options(...)` | Marks options disabled based on current selections |

Filter option lists are generated by functions in `boac/lib/cohort_utils.py`. Many are decorated with `@stow()` to cache expensive data-loch queries (e.g. `get_coe_profiles()`, `academic_plans_for_cohort_owner()`).

### API controllers

| File | Endpoints |
|------|-----------|
| `boac/api/cohort_controller.py` | `GET /api/cohort/<id>`, `POST /api/cohort/create`, `POST /api/cohort/update`, `DELETE /api/cohort/delete/<id>`, `POST /api/cohort/get_students_per_filters`, `GET /api/cohort/<id>/students_with_alerts`, `GET /api/cohort/<id>/events`, `GET /api/cohorts/by_dept_code/<dept_code>` |
| `boac/api/cohort_csv_controller.py` | `POST /api/cohort_csv/download`, `POST /api/cohort_csv/download_per_filters` |
| `boac/api/cohort_filter_options_controller.py` | `POST /api/cohort_filter_categories`, `POST /api/cohort_filter_options/translate` |

`_decorate_cohort(cohort)` in `cohort_controller.py` adds ownership flags, privacy warnings (when a non-owner views a cohort with department-restricted filters), and calnet-enriched owner metadata to every cohort response.

### Phantom cohorts

Ad-hoc searches (not yet saved) use a temporary `CohortFilter` object constructed in memory by `construct_phantom_cohort(domain, filters, **kwargs)` in `boac/api/util.py`. This object has `filter_criteria` set but no `id`; it is never persisted. `to_api_json()` is called on it identically to saved cohorts.

## Frontend layers

### API client

| File | Wraps |
|------|-------|
| `src/api/cohort.ts` | All CRUD and student-query endpoints |
| `src/api/cohort-filter-options.ts` | Filter category and translation endpoints |
| `src/api/cohort-csv.ts` | CSV export endpoints |

All methods in `src/api/cohort.ts` also update `currentUser.myCohorts` in the context store as a side effect after create/update/delete operations.

### Pinia store — `src/stores/cohort-edit-session/index.ts`

`useCohortStore` holds the entire mutable state of the cohort currently being viewed or edited:

**Key state fields**

| Field | Purpose |
|-------|---------|
| `cohortId` / `cohortName` | Identity of the loaded cohort |
| `domain` | `'default'` or `'admitted_students'` |
| `editMode` | `null`, `'add'`, `'apply'`, `'edit-N'`, or `'rename'` |
| `filters` | Current filter selections (UI array format) |
| `originalFilters` | Deep copy stashed for reset |
| `filterCategories` | Available filters for this domain/user |
| `students` | Current page of student results |
| `totalStudentCount` | Total matching students |
| `isModifiedSinceLastSearch` | Tracks unsaved filter changes |
| `isOwnedByCurrentUser` | Controls edit affordances |
| `hasPrivateCohortFilterCriteria` | Shows privacy warning banner |

**Key actions:** `addFilter`, `removeFilter`, `updateExistingFilter`, `setEditMode`, `stashOriginalFilters`, `restoreOriginalFilters`, `updateSession`, `setCurrentPage`.

**Key getters:** `showApplyButton` (filters changed, non-empty), `showSaveButton` (filters unchanged from last apply).

Orchestration logic (loading a cohort, applying filters, resetting) lives in `src/stores/cohort-edit-session/cohort-edit-session-utils.ts` rather than directly in the store to keep the store focused on state.

### Global context store — `src/stores/context.ts`

`currentUser.myCohorts` holds the list of saved cohorts shown in the sidebar. Mutations: `addMyCohort`, `removeMyCohort`, `updateMyCohort`.

### Vue components

| Component | Role |
|-----------|------|
| `src/views/Cohort.vue` | Main page: filter panel + student results table; handles sorting, term selection, curated group integration |
| `src/views/CohortHistory.vue` | Membership change history (added/removed students with timestamps) |
| `src/components/cohort/CohortPageHeader.vue` | Title, student count, owner info, show/hide filters toggle, rename/delete buttons |
| `src/components/cohort/FilterRow.vue` | One filter row; renders the correct input widget (select, range, boolean) based on `type.ux` |
| `src/components/cohort/FilterCategorySelect.vue` | Dropdown to pick which filter category to add |
| `src/components/cohort/FilterSelect.vue` | Single-select dropdown for a filter's value |
| `src/components/cohort/FilterSelectOptionGroups.vue` | Grouped dropdown for hierarchical options (e.g. academic standing by term) |
| `src/components/cohort/ApplyAndSaveButtons.vue` | Apply (execute search), Reset, Save, Save As buttons; triggers `CreateCohortModal` |
| `src/components/cohort/CreateCohortModal.vue` | Modal for naming and saving a new cohort |
| `src/components/cohort/RenameCohort.vue` | Inline rename for an existing cohort |

### TypeScript types

Defined in `src/lib/types-cohorts.ts`:

```typescript
type Cohort = { domain: string; id: number; name: string; totalStudentCount: number }
type FilterOption = { disabled: boolean; label: FilterOptionLabel; key: string; name: string; value: object }
type FilterOptionLabel = { primary: string; range: string[]; rangeMinEqualsMax: string }
```

Cohort name validation (duplicate check, reserved name check, length limit) lives in `src/lib/cohort.ts`.

## Data flow

### Ad-hoc search (unsaved)

```
FilterRow components
  → useCohortStore.filters (UI array)
  → [user clicks Apply]
  → POST /api/cohort/get_students_per_filters  {domain, filters, orderBy, ...}
  → cohort_controller: is_unauthorized_search / is_unauthorized_domain checks
  → translate_filters_to_cohort_criteria()  (UI array → JSONB dict)
  → construct_phantom_cohort()  (in-memory CohortFilter, no id)
  → CohortFilter.to_api_json()  (executes SQL against data_loch)
  → {students, totalStudentCount, ...}
  → useCohortStore.updateSession()
```

### Saving a cohort

```
[user clicks Save, enters name in CreateCohortModal]
  → POST /api/cohort/create  {domain, name, filters}
  → CohortFilter.create()  (inserts row, translates filters to criteria)
  → CohortFilter.update_sids_and_student_count()  (caches SIDs)
  → CohortFilter.track_membership_changes()  (writes CohortFilterEvent rows)
  → {id, name, criteria, totalStudentCount, alertCount, ...}
  → context store: addMyCohort()
```

### Loading a saved cohort

```
Route to /cohort/:id
  → GET /api/cohort/{id}?includeStudents=true
  → CohortFilter.find_by_id() + CohortFilter.to_api_json()
  → {id, name, criteria, students, owner, ...}
  → cohort-edit-session-utils.loadCohort()
      → POST /api/cohort_filter_options/translate  {domain, ownerUid, criteria}
      → CohortFilterOptions.translate_to_filter_options()  (JSONB dict → UI array)
      → POST /api/cohort_filter_categories  (load available options, mark disabled)
  → useCohortStore.updateSession()
```

### Updating available filter options

```
[user adds a filter]
  → POST /api/cohort_filter_categories  {domain, ownerUid, existingFilters}
  → CohortFilterOptions.get_customized_filter_categories()
      → populate_cohort_filter_options()  (already-selected values marked disabled)
  → {options: [{label, key, type, disabled, options: [...]}, ...]}
  → useCohortStore.setFilterCategories()
```
