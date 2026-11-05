# Degree progress

Degree progress, also called "degree checks", lets COE advisors build reusable **degree templates**: unit requirements plus a tree of categories laid out in three columns. They then copy a template onto a student as a **degree check** and assign the student's SIS courses to the template's requirements. All of it lives in the `boac` DB. The only things read from the data loch are the student's enrollments and grades, and student names.

Who can read and who can edit is covered in `.claude/docs/permissions.md` (`canReadDegreeProgress` / `canEditDegreeProgress`, the decorators, and the session cache). This doc covers only what's specific to degree progress.

## Vocabulary

- **Template vs. degree check.** Both are rows in `degree_progress_templates` (`DegreeProgressTemplate`).
  - A **template** has `student_sid IS NULL` and `parent_template_id IS NULL`.
  - A **degree check** has `student_sid` set and `parent_template_id` pointing at the template it was cloned from (`_clone_template` in `boac/api/degree_progress_api_utils.py`).
  - Child tables call the same ID by three names: `template_id`, `degree_check_id` (on courses), and `templateId`.
- **Clone.**
  - `clone()` / `clone_degree_template()` deep-copies unit requirements, categories, parent links, and category↔unit-requirement links.
  - `POST /api/degree/<id>/clone` with a `name` makes a new template. `POST /api/degree/check/<sid>/create` makes a student check.
  - The degree note and per-student category fields (`is_recommended`, `is_ignored`, `note`) are **not** copied (`_clone_categories`).
- **Transfer placeholders.** A template category with `is_satisfied_by_transfer_course=True` is cloned onto a student check with the flag set to False. A manual course (`grade='T'`, `accent_color='Purple'`, units from the lower bound of `course_units`) is created and assigned to it (`_clone_transfer_courses` and the matching block in `_bulk_clone_all`).
- **Category types** are the ENUM `degree_progress_category_types` (`boac/models/degree_progress_category.py`):
  - `Category`: top level only. It holds course requirements *or* subcategories, never both (`_can_accept_course_requirements`).
  - `Subcategory`: its parent must be a `Category`.
  - `Course Requirement`: its parent is a Category or Subcategory, and it holds at most one course.
  - `Placeholder: Course Copy`: created automatically when a course is copied or manually created into a category (`_create_placeholder_category_and_assign`), and deleted automatically when its course is moved or deleted (`assign_course`, `delete_course`).
  - `Campus Requirement, Unsatisfied | Satisfied`: no courses. Toggled via `/satisfy`.
  - `'Campus Requirements'` is a pseudo-type that exists only in the request. `_create_category` turns it into a `Category` with three Unsatisfied children.
- **Layout.** `ux_position_x` is the column (1–3, `_is_valid_ux_position_x`), and a child must match its parent's column. `ux_position_y` sets the order: higher values sort first (`get_categories._sort`), and new rows get `min - 1`. Move up/down swaps `y` with a sibling (`_move_category`).
- **Unit requirements.** `degree_progress_unit_requirements` holds `(name, min_units)` per template; the name is unique per template. They map to categories through `degree_progress_category_unit_requirements` and to courses through `degree_progress_course_unit_requirements`.
  - `DegreeProgressCourse.assign` copies the category's unit requirements onto the course at assign time.
  - "Completed" totals are calculated **client-side**: `getUnitsCompleted` in `src/components/degree/UnitRequirements.vue` sums the `units` of assigned courses.
- **Course buckets.** `to_api_json(include_courses=True)` returns these from `_get_partitioned_courses_json`:
  - `assigned`: `category_id` is set.
  - `ignored`: `ignore=True`. The UI calls this "Other Coursework".
  - `unassigned`: everything else.
  - `inProgress`: raw SIS sections from the current term with no grade. These aren't saved.
- **Copies and manual courses.**
  - A course's identity key is `section_id_term_id_manually_created_at_manually_created_by` (`_get_degree_progress_courses`, and `getCourseKey` in `src/lib/degree-progress.ts`).
  - The oldest row with a given key, by `(created_at, id)`, is the primary course. Later rows are copies (`isCopy`), made by `POST /api/degree/course/copy`.
  - Manual courses (`POST /api/degree/course/create`) have `section_id`/`term_id` NULL and `manually_created_*` set.
  - `delete_course` deletes only copies, or a manual primary course together with all its copies.
- **Degree note.** At most one `degree_progress_notes` row per check (PK `template_id`), upserted by `DegreeProgressNote.upsert`.
- **"Current" check.** `DegreeProgressTemplate.find_by_sid` sorts a student's non-deleted checks by `updated_at DESC`, and index 0 gets `isCurrent`. `redirect_to_student_degree_progress` and the batch exclusion query (`get_student_degree_checks_by_parent_template_id`) use the same rule.
- **Archive** means different things for checks and templates. See Gotchas.

## Tables and models (`boac/models/degree_progress_*.py`)

| Table / model | Key columns | Notes |
|---|---|---|
| `degree_progress_templates` / `DegreeProgressTemplate` | `degree_name`, `student_sid`, `parent_template_id` (self-FK), `advisor_dept_codes[]`, `archived_at`, `deleted_at`, `created_by`/`updated_by` → `authorized_users.id` | The only table with soft delete (`delete()` sets `deleted_at`; `find_by_id`, `find_by_name`, and `get_all_templates` filter it out). `advisor_dept_codes` is written at create time but never read. |
| `degree_progress_categories` / `DegreeProgressCategory` | `category_type`, `parent_category_id` (self-FK, ON DELETE CASCADE), `template_id`, `course_units` (NUMRANGE `[]`), `description`, `grade`, `note`, `accent_color`, `is_recommended`, `is_ignored`, `is_satisfied_by_transfer_course`, `ux_position_x/y` | Hard delete. `get_categories()` builds the nested JSON (`subcategories`, `courseRequirements`, `courses`). |
| `degree_progress_courses` / `DegreeProgressCourse` | `degree_check_id`, `category_id`, `sid`, `term_id`, `section_id`, `display_name`, `grade`, `units`, `ignore`, `note`, `accent_color`, `manually_created_at/by` | Hard delete. The unique key is `(category_id, degree_check_id, manually_created_at, manually_created_by, section_id, sid, term_id)`, per migration `2021/20210727-BOAC-4199`. `schema.sql` still shows an older version (see Gotchas). |
| `degree_progress_unit_requirements` | `template_id`, `name`, `min_units`, `created_by`, `updated_by` | `UNIQUE(name, template_id)` |
| `degree_progress_category_unit_requirements`, `degree_progress_course_unit_requirements` | composite-PK join tables | FKs are `ON DELETE CASCADE` (bottom of `scripts/db/schema.sql`) |
| `degree_progress_notes` / `DegreeProgressNote` | `template_id` (PK), `body`, `updated_by` | |

All FKs to templates and categories are `ON DELETE CASCADE` in SQL. The models declare no ORM cascades, so the delete helpers remove child rows by hand (`DegreeProgressCategory.delete`, `DegreeProgressUnitRequirement.delete`).

## API (all under `/api/degree…`)

Every route is decorated with `@can_read_degree_progress` (GET) or `@can_edit_degree_progress` (everything else). There is **no** department or student scoping beyond that. Most edits call `validate_template_not_archived()` and then `DegreeProgressTemplate.refresh_updated_at()`.

**Templates and unit requirements** (`degree_progress_controller.py`):

- **Read:** `GET /degree/templates`, and `GET /degree/<id>` (includes courses and adds `parentTemplateUpdatedAt`).
- **Create, rename, clone:** `POST /degree/create`, `POST /degree/<id>/update` (the name must be unique, case-insensitively, among non-deleted templates; see `validate_template_upsert`), `POST /degree/<id>/clone`.
- **Archive and delete:** `POST /degree/archive|unarchive` (body `templateId`; a student check also needs `is_admin_or_director`), `DELETE /degree/<id>` (soft delete).
- **Unit requirements:** `POST /degree/<id>/unit_requirement`, `POST /degree/unit_requirement/<id>/update`, `DELETE /degree/unit_requirement/<id>`.

**Categories** (`degree_progress_category_controller.py`):

- `POST /degree/category/create`: validates the parent and type rules and the x-position.
- `POST /degree/category/<id>/update`.
- `POST /degree/category/<id>/recommend`: per-student fields `isRecommended`, `isIgnored`, `grade`, `note`, `accentColor`, and units.
- `POST /degree/category/<id>/satisfy`.
- `DELETE /degree/category/<id>`.
- `GET /degree/category/<id>/move_up|move_down`: these GET routes change data.

**Student checks and courses** (`degree_progress_student_controller.py`):

- **Read:** `GET /degrees/student/<sid>` (history, with CalNet names), and `GET /degree/student/<sid>/redirect` (to the current check, or to `/student/<uid>/degree/create|history`; used by `goToStudentDegreeChecks` in `src/lib/utils.ts`).
- **Create checks:**
  - `POST /degree/check/<sid>/create`.
  - `POST /degree/check/batch` (`{sids, templateId}`), limited to `DEGREE_CHECK_BATCH_STUDENT_LIMIT` (1000 in `config/default.py`). `create_batch_degree_checks` bulk-inserts in chunks of 100.
  - `POST /degree/<template_id>/students`: returns the students whose *current* check came from this template, so the batch UI can exclude them.
- **Courses:** `POST /degree/course/<id>/assign` (`categoryId`, or none plus `ignore`), `POST /degree/course/copy`, `POST /degree/course/create`, `POST /degree/course/<id>/update`, `DELETE /degree/course/<id>`.
- **Note:** `POST /degree/<id>/note`.

## How SIS courses get in

There's no background job. Courses are synced **on every `GET /api/degree/<id>`** for a student check, in `DegreeProgressTemplate._get_partitioned_courses_json`:

1. `_get_enrollment_sections` calls `data_loch.get_enrollments_for_sid` (terms ≥ `LEGACY_EARLIEST_TERM`), passes the result through `boac/merged/student.merge_enrollment_terms`, and keeps only enrollments whose `academicCareer` is `UGRD` or `UCBX`.
2. For each section, the matching key is `ccn_termId_None_None`:
   - **Matches existing rows:** if the SIS grade differs, the grade is overwritten (`update_grade`), including on copies.
   - **No match, primary section with a grade:** a new unassigned `DegreeProgressCourse` row is created with the SIS units.
   - **No match, current-term primary section with no grade:** it goes into `inProgress` (not saved).
   - **Anything else** (non-primary sections, past-term rows with no grade) is ignored.
3. Rows with no SIS match (manual courses, or courses that disappeared from SIS) are still returned.

Units come from SIS at create time and aren't re-synced. `sis.units` is returned so the UI can flag edited units (`unitsWereEdited` in `src/lib/degree-progress.ts`). `copy_course` gets its units from `boac/merged/sis_sections.get_sis_section`.

## Permissions specifics

- `authorized_users.degree_progress_permission` is `'read' | 'read_write' | NULL`. Admins are forced to `read_write` in `UserSession`.
- The value is kept only for users in `COENG` (`_update_or_create_authorized_user` in `boac/api/user_controller.py`).
- **Refresh job** (`refresh_department_memberships` → `_get_degree_progress_permissions` in `boac/api/cache_utils.py`):
  - The value comes from `data_loch.get_advisor_uids_for_affiliations`: `UCOE` gives `read`, upgraded to `read_write` if the dept is `EDESS`/`EDDNO` or the advisor type is `DNDS`.
  - It's applied only when `automate_degree_progress_permission` is true. That flag defaults to `dept_code == 'COENG'` for new users.
- Locking a student check (archive) needs admin or director. This is checked server-side and mirrored by the toggle in `StudentDegreeCheckHeader.vue`.

## Frontend

- **Routes** (`src/router.ts`, guard `$_requiresDegreeProgress`):
  - `/degrees` → `ManageDegreeChecks.vue` (templates and archived templates, via `DegreeTemplatesDataTable.vue`).
  - `/degree/new` → `CreateDegreeTemplate.vue`.
  - `/degree/:id` → `DegreeTemplate.vue` (redirects to `/student/degree/:id` if `sid` is set).
  - `/degree/batch` → `BatchDegreeCheck.vue` (SIDs plus cohorts and curated groups; template picker `DegreeTemplatesMenu.vue`).
  - `/student/:uid/degree/create|history` → `StudentDegreeCreate.vue` / `StudentDegreeHistory.vue`.
  - `/student/degree/:id` → `StudentDegreeCheck.vue`.
  - `/degree/:id/print` → `PrintableDegreeTemplate.vue` (outside `StandardLayout`, `meta.printable`).
- **API client:** `src/api/degree.ts` has one function per endpoint. `getStudents` cancels the previous in-flight request.
- **Store** (`src/stores/degree-edit-session/index.ts`, `useDegreeStore`): holds the loaded template, `disableButtons`, `draggingContext {course, dragContext, target}`, and `includeNotesWhenPrint`. `degree-edit-session-utils.ts` has `refreshDegreeTemplate` (refetch, then `resetSession`; called after almost every change), `onDrop`, `deleteCategory`, and `deleteCourse`.
- **Components:** `TemplateCategoryColumn.vue` → `Category.vue` → `CoursesTable.vue`. Also:
  - Editing: `EditCategory.vue`, `UnitRequirements.vue` / `EditUnitRequirement.vue`, `SelectUnitFulfillment.vue`, `UnitsInput.vue`.
  - Ordering: `CategoryControlPositionY.vue` (move buttons).
  - Student-only (`components/degree/student/`): `CampusRequirementCheckbox`, `CreateCourseModal`, `EditCourse`, `EditCourseRequirement`, `AccentColorSelect`.
- **Helpers:** `src/lib/degree-progress.ts` has `flattenCategories`, `categoryHasCourse`, `getItemsForCoursesTable`, `validateUnitRange` (`MAX_UNITS_ALLOWED = 10`), and `validateDegreeTemplateName`.
- **Drag and drop** uses native HTML5 `draggable` / `dragstart` / `drop`.
  - Rows are dragged from `CoursesTable.vue` (assigned) and `UnassignedCourses.vue` (unassigned and ignored).
  - Drop zones are in `Category.vue`, `CoursesTable.vue`, and the two zones in `StudentDegreeCheck.vue`.
  - `onDrop` maps `"<from> to <to>"` onto `assignCourse`. `StudentDegreeCheck.scrollTo` auto-scrolls during a drag (except in Firefox).
- **Keyboard and single-pointer alternative to dragging (WCAG 2.2, 2.5.7):** `student/CourseAssignmentMenu.vue` is a button that opens a menu of every valid target, plus "Unassign" and "Other Coursework".
  - It renders for every course in `UnassignedCourses.vue`, but in `CoursesTable.vue` only when `bundle.course.categoryId` is set.
  - Copying uses `DuplicateExistingCourse.vue` (a select plus a button). Reordering categories uses buttons, not dragging.
  - Any new drag interaction must come with an equivalent like this (see `src/CLAUDE.md`).
- **Print:** the link is built in `StudentDegreeCheckHeader.vue` (`?includeNote=`) and `DegreeTemplatesDataTable.vue`. The print view reuses `Category`, `CoursesTable`, and `UnitRequirements` with `printable`, uses `@page { size: landscape }`, and shows an "UNOFFICIAL DEGREE PROGRESS REPORT" banner.

## Tests

- **Files:** `tests/test_api/test_degree_progress_controller.py`, `test_degree_progress_category_controller.py`, `test_degree_progress_student_controller.py`. Fixtures are defined in each file (`mock_template`, `mock_degree_check`, `mock_degree_course`, `mock_degree_checks`, `mock_note`, `mock_unit_requirement`).
- **Test UIDs:**
  - `2040`: admin.
  - `1133399`: COENG `read_write`, the main editor.
  - `6972201`: COENG `read`.
  - `9933311`: COENG director (can lock student checks).
  - `90412`: COENG, no degree access.
  - `53791`: QCADV director, no degree access; used as the unauthorized user.
- **Student data:** student-side tests use one synthetic loch fixture student, via the `coe_student_sid` / `coe_student_uid` constants. Refer to it by those constant names only.
- **Changing loch data:** `_change_grade_in_data_loch` rewrites `student.student_enrollment_terms` in the test loch to exercise grade sync.
- **Batch at scale:** `test_create_batch_at_scale` raises the batch limit to 5000 using placeholder SIDs and asserts it runs in under 120 seconds.
- **Browser tests:** `bea/tests/test_degree_check_mgmt.py`, `test_degree_check_courses.py`, `test_degree_check_unit_reqts.py`.

## Gotchas

- **`GET /api/degree/<id>` writes to the DB.** It updates grades and inserts course rows. Don't cache it, and expect writes inside read tests.
- **`isCurrent` follows `updated_at`.** Any edit to an older check calls `refresh_updated_at`, which makes it the current check. The same rule decides which students a batch excludes. A new endpoint that changes a check must call `refresh_updated_at`, or the history and current-check logic drift.
- **"Archive" has two meanings.**
  - On a student check it means **locked**: admin or director only, and `validate_template_not_archived` blocks edits.
  - On a template it only **hides** the template in the UI (any editor can do it). Archived templates stay editable and can still be used for single or batch checks (`DegreeTemplatesMenu.vue` lists them in an optgroup).
- **Deleting a category hard-deletes the courses assigned to it** (`DegreeProgressCategory.delete`), and child categories go with it through the SQL cascade. SIS courses come back as *unassigned* on the next load; manual courses, copies, and per-course notes, units, and colors are lost.
- **Manual grade edits on SIS courses are overwritten** by the SIS grade on the next load. Unit edits survive.
- **Changing a category's unit requirements** (`DegreeProgressCategory.update`) doesn't update courses already assigned to it, because their mappings were copied at assign time.
- **Batch commits each chunk of 100 separately** (`create_batch_degree_checks`), so a failure partway through leaves earlier chunks committed. Batch and single create don't check that the SIDs exist in the loch.
- **No department or student scoping.** Any `canReadDegreeProgress` user can read any check by ID or SID, and any editor can soft-delete a student check (`delete_template` has no director check, unlike archive).
- **`move_up`/`move_down` are GET routes that change data.**
- **Several user-entered fields are rendered with `v-html`** (template names, degree notes, course and category notes, category descriptions). Don't add new `v-html` uses for user input.
- **`scripts/db/schema.sql` has drifted from the migrations and models for these tables** (e.g. the `degree_progress_courses` unique constraint and `grade` nullability). Check `scripts/db/migrate/` and the model before trusting a constraint in `schema.sql`.
