# Curated groups

A curated group is a hand-picked, named list of SIDs owned by one advisor. A cohort (`.claude/docs/cohorts.md`), by contrast, is a saved set of filters evaluated against the data loch. A curated group's membership is stored in the BOA database and changes only when someone adds or removes a student, or when the nightly cleanup drops SIDs that are no longer available. The backend calls it `CuratedGroup` (`boac/models/curated_group.py`), but the tables are named `student_groups` and `student_group_members`.

## Curated groups vs cohorts

| | Curated group | Cohort |
|---|---|---|
| Membership | Explicit SIDs in `student_group_members` | Computed from `filter_criteria` |
| Domains | `default` / `admitted_students` (same `cohort_domain_types` ENUM) | same |
| Change tracking | None (no events table) | `cohort_filter_events` |
| Link between them | A cohort can filter on `curatedGroupIds` ("My Curated Groups") | — |

- **"My Students"** is a *cohort filter* (`cohortOwnerAcademicPlans`, translated in `boac/models/cohort_filter.py`), not a curated group. `boac/models/development_db.py` happens to seed empty curated groups *named* "My Students", but nothing in the code treats that name specially.
- The admitted-students domain is gated the same way as for cohorts: `is_unauthorized_domain()` on create, and `current_user.can_access_admitted_students` on view. These are two different CE3 checks; see the Gotchas in `.claude/docs/permissions.md`.

## Data model (`scripts/db/schema.sql`, `boac/models/curated_group.py`)

```sql
student_groups (id, domain cohort_domain_types NOT NULL, name VARCHAR(255) NOT NULL,
                owner_id INTEGER NOT NULL REFERENCES authorized_users ON DELETE CASCADE,
                created_at, updated_at,
                UNIQUE (owner_id, name))          -- student_groups_owner_id_name_unique_constraint
student_group_members (student_group_id INTEGER REFERENCES student_groups ON DELETE CASCADE,
                       sid VARCHAR(80) NOT NULL,
                       PRIMARY KEY (student_group_id, sid))   -- indexes on both columns
```

- `CuratedGroup` maps `student_groups`. `CuratedGroupStudent` maps `student_group_members`, with the Python attribute `curated_group_id` stored in the column `student_group_id`.
- **Hard delete only.** There's no `deleted_at`. `CuratedGroup.delete()` deletes the row (members cascade), then calls `CohortFilter.delete()` on every cohort returned by `get_referencing_cohort_ids()`. **Cohorts that use the group as a filter are deleted too** (tested in `test_cohort_controller.py`).
- `get_referencing_cohort_ids()` scans only cohorts owned by the *group owner* whose `filter_criteria->>'curatedGroupIds'` contains `self.id`.
- There are no sharing or ACL columns. Visibility rules live in the controller.

## Visibility and ownership (`boac/api/curated_group_controller.py`)

- **Reading** (`GET /<id>`, `students_with_alerts`, `download_csv`) goes through `_can_current_user_view_curated_group()`. Access is allowed for admins, or when the owner has at least one department membership AND (the domain is `default` OR the viewer `can_access_admitted_students`). The viewer does **not** need to share a department with the owner. A group owned by an admin with no departments is therefore 403 to non-admins (`test_advisor_cannot_see_admin_curated_group`).
- **Writing** (add, remove, rename, delete) is owner-only (`owner_id != current_user.get_id()`). Admins get no exemption.
- **"Everyone's Curated Groups"** (`/all/curated_groups` → `src/views/BrowseAllGroups.vue`, shared with `/all/cohorts` via `meta.groupsType`) calls `GET /api/curated_groups/by_dept_code/<dept_code>` → `CuratedGroup.get_curated_groups_owned_by(uids, include_admitted_students)`. Any advisor can browse any department's groups. Owners without a CalNet record are skipped, and results are sorted by owner name.

## API (all `@advisor_required`)

| Purpose | Endpoint | Notes |
|---|---|---|
| Browse | `GET /api/curated_groups/by_dept_code/<dept_code>` | `[{...calnetUser, curatedGroups: [{id, domain, name, ownerUid, sids, totalStudentCount}]}]` |
| Create | `POST /api/curated_group/create` `{domain, name, sids?}` | 403 on an unauthorized domain, 400 without a name. Non-digit SIDs are silently dropped (`sid.isdigit()`). Returns students and `alertCount` |
| View | `GET /api/curated_group/<id>?offset&limit&orderBy&termId` | Defaults 0 / 50 / `last_name`. Adds `ownerName`, `ownerUid`, `ownerDeptCodes` when the viewer isn't the owner, and `referencingCohortIds` |
| Alerts | `GET /api/curated_group/<id>/students_with_alerts` | Only students with alerts, as profile summaries plus `alertCount` (used by `SortableGroup.vue` on Home) |
| CSV | `POST /api/curated_group/<id>/download_csv` `{csvColumnsSelected, termId}` | `response_with_students_csv_download()` over all SIDs (`boac/api/csv_file_download_utils.py`) |
| Add | `POST /api/curated_group/students/add` `{curatedGroupIds, sids, returnStudentProfiles}` | 404/403 per group. Returns one JSON per group plus `alertCount` |
| Remove | `POST /api/curated_group/remove_student/<sid>` `{curatedGroupIds}` | Unknown IDs are skipped (`find_by_ids`). Returns the updated groups |
| Rename | `POST /api/curated_group/rename` `{id, name}` | A non-owner or missing group gets **400**, not 403 |
| Delete | `DELETE /api/curated_group/delete/<id>` | 404 / 403 / 200. Also deletes referencing cohorts |

**SID limits:** the server enforces none beyond `isdigit()` and de-duplication (`CuratedGroupStudent.add_students()` skips existing members). It doesn't check that SIDs exist; the UI does that first with `POST /api/students/validate_sids` (in `BulkAddSids.vue`).

## Loading student data

- `CuratedGroup.to_api_json(include_students, order_by, offset, limit)` reads all SIDs from the BOA DB (`totalStudentCount = len(sids)`). For the current page:
  - `default` domain: `query_students(sids=..., academic_career_status='all', include_profiles=False, order_by, offset, limit)` (`boac/merged/student.py` → `data_loch.get_students_query`). `'all'` keeps inactive and completed students (`TestCuratedGroupWithInactives`).
  - `admitted_students` domain: `boac/merged/admitted_student.get_admitted_students_by_sids()`.
- `_curated_group_with_complete_student_profiles()` then fills in that page with full data: `get_student_profile_summaries(sids, term_id)` for `default` (keeping the sorted order, and merging ASC/COE data according to `get_student_query_scope()`), or a second admit query. Then `_include_alert_counts()` runs.
- **Alert counts:** `alert_counts_for_curated_group(viewer_id, group_id)` (`boac/api/util.py`) is `@stow('alert_counts_curated_group_{group_id}_user_{viewer_id}')` over `Alert.current_alert_counts_for_curated_group()`, counting current-term alerts the *viewer* hasn't dismissed. See `.claude/docs/alerts.md`.
  - Add, remove, and delete clear `alert_counts_curated_group_{id}_%`. Dismissing an alert calls `clear_cached_alert_counts_for_owner(alert_id, user_id)`.
  - `refresh_alerts()` in `boac/api/cache_utils.py` clears all of them and re-warms the cache for each `default` group's owner.
- **Cleanup:** `update_curated_group_lists()` (`boac/api/cache_utils.py`, run from `load_term()` for the current term) loads every group's SIDs via `data_loch.get_student_profiles()` or `get_admitted_students_by_sids()`, and calls `CuratedGroup.remove_student()` for SIDs missing from the loch.
- **Cohort side effects:** every add or remove calls `_refresh_related_cohorts()`, which clears the cached SIDs and counts of each referencing cohort and re-runs `to_api_json(include_alerts_for_user_id=owner)`. That also writes `cohort_filter_events`.

## Integrations

- **Cohort filter:** `curatedGroupIds` options come from `curated_group_options(user_id)` (`boac/lib/cohort_utils.py`), limited to the owner's **`default`-domain** groups. In `get_students_query`, the selected groups' members are combined (`student_group_id = ANY(...)`) into an `spi.sid = ANY(...)` filter. Note that this reads the BOA DB from inside the loch query builder.
- **Batch notes:** `_get_sids_for_note_creation()` (`boac/api/notes_controller.py`) unions `sids`, `cohortIds`, and `curatedGroupIds` (`CuratedGroup.get_all_sids`). In the UI, `BatchNoteFeatures.vue` offers only non-admit groups. See `.claude/docs/notes-and-search.md`.
- **Batch degree checks:** `BatchDegreeCheck.vue` lists `default` groups in `BatchAddStudentSet.vue`, then resolves them with `POST /api/students/distinct_sids` (`get_distinct_sids()`, which checks group ownership). `POST /api/degree/check/batch` receives only SIDs. See `.claude/docs/degree-progress.md`.
- **Session:** `get_my_curated_groups()` (`boac/api/util.py`) puts `myCuratedGroups` into `/api/profile/my`: every owned group, including **all `sids`**, plus `alertCount`, sorted by name.
- **CSV "Curated Groups" column:** names of the current user's `default` groups that contain each student (`get_current_user_curated_groups_containing`).

## Frontend

| File | Role |
|---|---|
| `src/api/curated.ts` | Wraps every endpoint. After a change it re-fetches the whole profile (`$_onUpdate` → `getUserProfile`) and broadcasts `my-curated-groups-updated` with the domain |
| `src/stores/curated-group/index.ts` | `useCuratedGroupStore`: id, name, domain, owner, page, `itemsPerPage` (50), `referencingCohortIds`, students, and `mode` (`bulkAdd` or `rename`; anything else throws) |
| `src/views/CuratedGroup.vue` (`/curated/:id`) | Header, term selector and sort, pagination, `StudentRow` (`listType` `curatedGroupForOwner` shows a remove button), `AdmitStudentsTable` for admits, and `BulkAddSids` in `bulkAdd` mode |
| `src/views/CreateCuratedGroup.vue` (`/curate?domain=`) | `BulkAddSids` → `CreateCuratedGroupModal` → `createCuratedGroup` → redirect |
| `src/components/curated/CuratedGroupHeader.vue` | Owner info, add/rename/delete (owner only), export. Delete is **blocked in the UI** while `referencingCohortIds` is non-empty |
| `CreateCuratedGroupModal.vue`, `RenameCuratedGroup.vue` | Name validation via `validateCohortName()` (`src/lib/cohort.ts`): 255 characters, unique (case-insensitive) across both cohorts and curated groups, plus reserved UWASC names |
| `dropdown/ManageStudent.vue` | Per-student menu (`menuitemcheckbox` items). Membership comes from `myCuratedGroups[].sids` |
| `dropdown/CuratedGroupSelector.vue` + `CuratedStudentCheckbox.vue` | Bulk "select all on page, add to groups". They coordinate through context-store events `curated-group-checkbox-(un)checked` and `curated-group-(de)select-all` |
| `src/components/util/BulkAddSids.vue` | Paste SIDs, check they're numeric, `validateSids`, and offer to remove those not found (listing them if there are 15 or fewer) |

**Accessibility patterns to keep:**

- Every action is announced with `alertScreenReader` (adding, added, removed, canceled, renamed).
- Focus returns with `putFocusNextTick` to the control that started the action: the menu button, the `add-all-to-*` checkbox, `delete-curated-group-button`, or the textarea.
- Menu items toggle on Space (`@keydown.space.prevent`); Apply and Create respond to Enter.
- SIDs are read aloud as "S I D" through `sr-only` text and aria-labels.
- In student rows, the `ManageStudent` menu stays in the DOM but is transparent (`opacity-zero`) until the row is hovered **or receives keyboard focus** (`@focusin` / `@focusout` in `StudentRow.vue`). Keep both triggers so keyboard users can see what they've focused.

## Tests

- `tests/test_api/test_curated_group_controller.py` covers create, get (auth, sort orders, profiles, ASC data hiding), students_with_alerts, add, remove, rename, delete, inactive students, and CSV. Local helpers are `_api_curated_group_create` and `_api_get_curated_group`.
- `tests/test_api/api_test_utils.py` has `api_curated_group_add_students()` and `api_curated_group_remove_student()`, both calling `std_commit(allow_test_environment=True)`.
- Related: `test_cohort_controller.py` (`curatedGroupIds` filter and delete cascade), `test_cache_utils.py::test_update_curated_group_lists`, `test_cohort_filter_options_controller.py`, `test_alerts_controller.py`, `test_notes_controller.py`, `test_student_controller.py` (distinct SIDs).
- Fixture groups are seeded by `development_db._create_curated_groups()`: UID `6446` owns one empty group and one with 4 students; UID `1133399` one group with 2 students; UID `2525` one `admitted_students` group; admin `177473` an empty group.
- Test constants in this file: `admin_uid='177473'`, `asc_advisor_uid='6446'` (actually a UWASC *director*), `asc_director_uid='90412'`, `ce3_advisor_uid='2525'`, `coe_advisor_uid='1133399'`. See the UID table in `.claude/docs/permissions.md`. Refer to students as `<sid>`.

## Gotchas

- **Deleting a group deletes cohorts.** The UI stops owners from doing it, but the API deletes referencing cohorts without asking.
- **Every add or remove re-runs cohort queries.** `_refresh_related_cohorts` recomputes each referencing cohort synchronously, so it can be slow.
- **Multi-group add isn't atomic.** `students/add` commits each group in a loop, so a 403 or 404 on a later ID leaves the earlier groups already changed.
- **`totalStudentCount` can exceed the students listed.** It counts DB rows, while the page comes from the loch. SIDs missing from the loch disappear only after `update_curated_group_lists()`.
- **The session carries every SID.** `myCuratedGroups` includes every SID of every group, and `ManageStudent` relies on that. Large groups make `/api/profile/my` heavier.
- **Duplicate names hit a DB constraint.** `UNIQUE(owner_id, name)` is enforced only by the DB and the client; the API doesn't check first.
- **SIDs must be JSON strings.** `sid.isdigit()` is called on each SID, so integer SIDs raise an error.
- **`curatedGroupIds` in cohort criteria must be integers.** `get_referencing_cohort_ids()` uses `self.id in ...`, so string IDs wouldn't be detected.
- **Status codes vary.** Decorators return 401 and most inline checks return 403, but rename returns 400 for non-owners.
- **The admitted-students domain is left out in several places:** cohort filter options, batch notes, batch degree checks, and the CSV "Curated Groups" column.
- **Analytics category.** `src/api/curated.ts` tracks curated-group events with `ga.cohort`, not `ga.curated`.
