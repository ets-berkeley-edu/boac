# Peer advising

Peer advising lets student peer advisors write BOA notes about other students, under the supervision of staff advisors called peer advisor managers (PAMs). Each note, template, and membership belongs to a **peer advising department**, which is a sub-unit of a university department. Peer advisors have their own layout and routes (`/peer_advisor/*`). Managers use a dashboard inside the standard layout (`/peer/management/:id`).

Related docs (not repeated here):

- `.claude/docs/permissions.md`: roles, the `peer_advisor*` decorators, how memberships are merged into the session, and the test-user UID table.
- `.claude/docs/notes-and-search.md`: the note lifecycle, `note_topics`, comments, SQS/CDC, and the internals of peer advising search (`POST /api/search/peer_advising_notes`).

## Data model

| Table / model | Notes |
|---|---|
| `peer_advising_departments` (`boac/models/peer_advising_department.py`, `PeerAdvisingDepartment`) | `id`, `name`, `university_dept_id` (FK to `university_depts`, `ON DELETE CASCADE`). Lookups: `get_department_by_id`, `get_department_by_name`, `find_by_university_dept_id`. |
| `peer_advising_department_members` (`PeerAdvisingDepartmentMember`) | Roles and soft delete are covered in permissions.md. The PK is `(peer_advising_department_id, authorized_user_id)` (`scripts/db/schema.sql`), so a user has one role per department. |
| `peer_advising_topics` (`boac/models/peer_advising_topic.py`, `PeerAdvisingTopic`) | A pick-list separate from `topics`. The DB column is `VARCHAR(50) UNIQUE`; the model declares `String(255)`. Soft delete via `deleted_at`. |
| `notes.peer_advising_department_id`, `notes.note_template_id`, `note_templates.peer_advising_department_id` | Added in `scripts/db/migrate/2025/20250122-BOAC-5841/pre_deploy_01_peer_advising.sql`. A note or template is a peer one exactly when `peer_advising_department_id` is set. |

### How departments get created

There is **no API or admin UI** for creating a peer advising department.

- **Production:** SQL migrations under `scripts/db/migrate/`, e.g. `2025/20250507-BOAC-6184/peer_advising_dept_school_of_public_health.sql` and `2026/20260709-BOAC-6755/peer_advising_dept_economics.sql`. Both use the same pattern: `DELETE FROM peer_advising_departments WHERE name = ...`, then `INSERT ... SELECT ... FROM university_depts d WHERE d.dept_code = '<CODE>'`. Copy this pattern for new departments (see `scripts/db/CLAUDE.md`).
- **Dev/test:** `fixtures/development_db/peer_advising_departments.json`, loaded by `_create_peer_advising_departments()` in `boac/models/development_db.py`. It defines three departments with their members: Educational Opportunity Program and NAVCAL (both under `ZCEEE`), and Mechanical Engineering (under `COENG`).
- **Frontend list:** `GET /api/users/departments` calls `UniversityDept.get_all_departments(include_peer_advising_departments=True)`. `setCurrentUser()` in `src/stores/context.ts` flattens the result into `contextStore.allPeerAdvisingDepartments`, and `findPeerAdvisingDepartment()` in `src/lib/berkeley-department.ts` looks departments up there.
- **Topics** are also seeded only by SQL (`2025/20250326-BOAC-6056/pre_deploy_01_peer_advising_topics.sql`) or, in dev, by `_create_peer_advising_topics()`.

## What each role can do

| Action | Peer advisor | Peer advisor manager | Where |
|---|---|---|---|
| Create a note | Yes, own dept only | No: `peer_advisor_required` rejects managers | `create_peer_advising_note` |
| List dept notes | Yes | Yes | `GET /api/peer_advising/<dept_id>/notes`; the PA home page uses `GET /api/peer_advisor/<uid>/notes` (self or admin) |
| Edit a note | Own notes | Any note in their dept | `can_current_user_edit_note()` (`boac/merged/advising_note.py`) |
| Delete a note | No (no advising-data access) | Yes, via `DELETE /api/notes/delete/<id>` | `delete_note` (`notes_controller.py`); the UI button is gated by `isPeerAdvisorManager` in `PeerAdvisingNotesTable.vue` |
| Comment | `POST /api/peer_advising/note/add_comment` (own dept) | `POST /api/note/add_comment` (regular endpoint) | see "Peer advising notes" |
| Attachments | Add / download / remove | Same | `add_peer_advising_attachments`, `download_peer_advising_note_attachment`, `remove_peer_advising_note_attachment` |
| Look up students | Name/SID/email lookup, basic profile + active majors, enrollments | — | `GET /api/peer_advising/student/<sid>`, `GET /api/peer_advising/<sid>/enrollments` |
| Manage peer advisors, templates, reports | No | Yes, own dept | sections below |

## Peer advising notes (`boac/api/peer_advising_notes_controller.py`)

- **Created already published.** `create_peer_advising_note` calls `Note.create()` with `is_draft` left False; it never goes through `create_draft`.
  - `author_role` is the membership `role_type`, and `author_dept_codes` is `[university_dept_code]`.
  - The author's `NoteRead` row is created immediately.
  - The posted `peerAdvisingDepartmentId` must match one of the caller's memberships, or the call returns 403.
- **The body may be empty.** An empty body becomes `None`. In the regular `update_note`, the "subject required" rule is waived when `note.peer_advising_department_id` is set.
- **Topics** are plain strings chosen from `GET /api/peer_advising/note_topics` (`PeerAdvisingTopic.get_all()`), stored in `note_topics` like any other note's topics.
- **Templates:** `noteTemplateId` is saved as `notes.note_template_id`, which the template-usage report counts.
- **Updating:** `POST /api/peer_advising/note/update` (`update_peer_advising_note`) reads `request.form`. It always sets `is_draft=False`, runs `process_input_from_rich_text_editor` on the body, and adds a `student` block from `data_loch.get_student_by_sid`.
- **Attachments on create** are uploaded *after* the note is created, in a second call (`addPeerAdvisingAttachments` → `POST /api/peer_advisor/note/<id>/attachments`; see `src/stores/note-edit-session/note-edit-session-utils.ts`). `removeAttachment()` in `src/api/notes.ts` picks the peer endpoint when `note.peerAdvisingDepartmentId` is set.
- **Listing:** `_peer_advising_notes_api_json()` calls `Note.get_notes_by_peer_advising_department()`, which returns non-draft, non-deleted top-level notes ordered by `updated_at DESC`. The `peerAdvisorNotes=<uid>` query param filters by author (`ShowMyPeerAdvisingNotesToggle.vue`). `includeStudents=true` adds names from `get_basic_student_data`.
- **Comments** are `notes` rows with `parent_note_id` and `peer_advising_department_id` set.
  - On the peer endpoint, the department is the caller's *first* membership (`memberships[0]`).
  - On the regular endpoint, a manager's comment is stamped with their first `peer_advisor_manager` membership (`get_department_membership_with_role`). A non-manager's comment gets `None`.
- **Visibility:**
  - Peer advisors see only notes from departments where they hold `peer_advisor` (`can_current_user_access_note`).
  - Regular advisors with advising-data access see peer notes on the student timeline like any BOA note; `get_native_boa_notes()` doesn't filter them out.

## Managing peer advisors (`boac/api/peer_advising_users_controller.py`)

- **UI path:** `PeerAdvisorManager.vue`, "Account Management" tab → `PeerAdvisingAccountMgmt.vue` → `PeerAdvisingAddStudent.vue`.
- **Lookup is a *student* search:** `findStudentsByNameSidOrEmail` → `POST /api/students/find_by_name_sid_or_email`. Active peer advisors are filtered out by `csid`. If the selected student matches a deleted peer advisor, the button changes to "Restore".
- **Create:** `POST /api/peer_advising/create_peer_advisor` (`@peer_advisor_manager_in_department`, department taken from the POST body).
  - Calls `AuthorizedUser.create_or_restore(uid, can_access_advising_data=False, can_access_canvas_data=False, degree_progress_permission=None)`, then `create_or_update_membership(role_type='peer_advisor')`.
  - The UID isn't validated against CalNet. CalNet data comes in only when the response is built (`authorized_users_api_feed` → `calnet.get_calnet_users_for_uids`).
- **List:** `GET /api/peer_advising/department/<id>/<role_type>?includeDeleted=&includeNoteCounts=` (`get_peer_advising_department`). Note counts come from `Note.get_note_counts_per_uid`.
- **Delete:** `DELETE /api/peer_advising/delete_peer_advisor/<dept_id>/<user_id>` soft-deletes the membership **and** the whole `authorized_users` row (`AuthorizedUser.delete`).
- **Restore:** `GET /api/peer_advising/restore_peer_advisor/<dept_id>/<user_id>` calls `restore_membership`, then `create_or_restore(is_blocked=False)`.
- **Self-protection:** manager actions go through `is_authorized_peer_advisor_manager(..., peer_advisor_user_id=...)` (`boac/api/auth_utils.py`), which also stops a manager from acting on themselves.
- **Admin-wide list/CSV:** `POST /api/users/peer_advising` (`@admin_required`, `user_controller.get_peer_advising_users`). The SQL is in `_peer_advising_users_sql()` (`boac/models/authorized_user.py`).

## Templates and topics

`boac/api/peer_advising_note_templates_controller.py`:

| Endpoint | Guard |
|---|---|
| `POST /api/peer_advising/note_template/create` | `peer_advisor_manager_required`; admins and users with no advisor/director dept get 403 |
| `GET /api/peer_advising/note_template/<id>` | PA or PAM, and a member of the template's dept |
| `GET /api/peer_advising/note_templates/peer_advising_department_id/<id>` | `peer_advisor_or_peer_advisor_manager_in_department` |
| `POST /api/peer_advising/note_template/update`, `DELETE .../note_template/delete/<id>` | PAM, and a member (any role) of the template's dept |

- Peer templates are shared per department, not per creator. `NoteTemplate.get_templates_created_by()` excludes them, so they never show up in a manager's personal template list.
- Frontend: `PeerAdvisingNoteTemplates.vue` and `PeerAdvisingNoteTemplateModal.vue` (manager tab), `SelectPeerAdvisingNoteTemplateForNote.vue` (note modal), and `getNoteTemplatesForPeerAdvising` in `src/api/note-templates.ts`.
- `boac/api/topic_controller.py` manages only the regular `topics` table. Peer topics have no create or delete API; the only route is the read in `get_peer_advising_topics`. UI: `PeerAdvisingNoteTopics.vue`.

## Reports

All routes in `boac/api/peer_advising_reports_controller.py` use `@peer_advisor_manager_in_department`, so only admins and that department's managers can call them. The SQL lives in `boac/merged/peer_advising_notes_reports.py`.

| Endpoint | Content |
|---|---|
| `POST /api/peer_advising/<id>/notes/csv` | `get_all_peer_advising_notes()`: every top-level note with author, topics, and student name/email (`get_students_by_sids`); body newlines are collapsed |
| `GET /api/peer_advising/<id>/report/notes` | Current month by peer advisor (`_peer_advisors_with_note_counts`), plus `get_peer_advising_note_author_count`, `get_peer_advising_note_template_usage`, `get_peer_advising_note_topic_usage`, `get_total_peer_advising_notes` |
| `GET /api/peer_advising/<id>/report/historical` | Year → month → peer advisor counts, **excluding the current month** (`_historical_peer_advisors_with_note_counts`) |
| `POST /api/peer_advising/notes/authored_by` | Drill-down for one author (`Note.get_peer_advising_notes_authored_by`, which excludes private notes). Guarded only by `advising_data_access_required` |

- Per-advisor counts (`get_notes_created_by_peer_advisors`) include only `author_role = 'peer_advisor'`, and they include removed advisors (returned with `deletedAt`).
- Admins and directors also get a `peerAdvising` block from `GET /api/reports/notes/<dept_code>` (`admin_reports_controller.get_notes_report_by_dept`).
- Frontend: `src/components/peer/reports/` (`PeerAdvisorManagerReports.vue` → current month, historical, templates used, topics used, CSV). `src/lib/peer-advisor-sort.ts` holds `sortPeerAdvisors`, `partitionPeerAdvisors` (active vs. deleted), and the `aria-sort` helpers. Report types are in `src/lib/types-peer-advising.ts`.

## Frontend map

- **Routes (`src/router.ts`):**
  - `PeerAdvisor` layout (`src/layouts/PeerAdvisor.vue`, no sidebar): `/peer_advisor/home`, `/peer_advisor/:uid/home` (an admin's view of a given PA), `/peer_advisor/profile`, `/peer_advisor/search`, plus error and 404 routes.
  - `/peer/management/:id` (`PeerAdvisorManager.vue`) lives in `StandardLayout`; `HeaderMenu.vue` links to it.
  - Guards are described in permissions.md.
- **Views:**
  - `PeerAdvisorHome.vue`: `PeerAdvisingNotesDashboard`, fed by `getPeerAdvisorNotes`. The department is the user's first `peer_advisor` membership.
  - `PeerAdvisorSearch.vue`: `peerAdvisorSearch` in `src/api/search.ts`, `PeerAdvisingStudentsTable.vue`, `PeerAdvisingNotesTable.vue`.
  - `PeerAdvisorManager.vue`: tabs `accounts`, `templates`, `reporting`, and `dashboard`, selected by URL hash. `PeerAdvisorDashboardView.vue` reuses the PA dashboard via `getPeerAdvisingDepartmentNotes`.
- **Notes UI (`src/components/peer/note/`):** `EditPeerAdvisingNoteModal.vue` (student lookup, `CompactStudentCourseSchedule`, topics, template picker), `PeerAdvisingNotesTable.vue` (comments through the shared `AdvisingComments`), `NotesCreatedByPeerAdvisor.vue` (report drill-down).
- **API clients:** `src/api/peer-advising-notes.ts`, `peer-advising-users.ts`, `peer-advising-reports.ts`. Events broadcast: `peer-advising-note-created`, `peer-advising-note-updated`, `note-updated`.

## Tests

- Files: `tests/test_api/test_peer_advising_{notes,users,reports,note_templates,search}_controller.py`.
- Fixtures in `tests/conftest.py`:
  - `mock_eop_peer_advising_note`: authored by EOP peer advisor `1563405`.
  - `mock_navcal_peer_advising_note`: authored by `188444`.
  - `mock_navcal_peer_advising_manager_note`: authored by PAM `2525`, created directly with `Note.create` because no endpoint lets a PAM create one.
  - `mock_navcal_peer_advising_note_with_comments`: comments from peer advisors, PAMs (including another department's PAM, `1133399`), and a non-PAM advisor.
  - `mock_peer_advising_note_template`: a NAVCAL template created by `2525`.
  - The note fixtures call `refresh_loch_note_search_index()` so search tests work.
- Test UIDs by role:

  | Role | UIDs |
  |---|---|
  | Peer advisors | `1133400`, `188444` (NAVCAL); `1563405` (EOP); `1913062` (Mechanical Engineering) |
  | Peer advisor managers | `2525` (NAVCAL); `3535` (EOP); `1133399` (Mechanical Engineering) |
  | Non-PAM advisors | `5405613` (CE3); `53791` and `188242` (QCADV); `1022796` (no advising data) |
  | Admin | `2040` |

- Fixture SIDs and student names are synthetic. Don't copy them into docs or new fixtures; use placeholders such as `<sid>`.

## Gotchas

- **New departments can be invisible to the UI.** `get_all_departments()` joins `peer_advising_departments` through `university_dept_members`. If the parent university department has no active members, the peer department is missing from `allPeerAdvisingDepartments`, and `findPeerAdvisingDepartment()` throws.
- **"First membership" logic is common.** It appears in `memberships[0]` (`get_peer_advising_note`, `get_notes_for_peer_advisor`, `add_peer_advising_note_comment`), in `get_department_membership_with_role`, and in `PeerAdvisorHome.vue` / `PeerAdvisorSearch.vue`. All of it assumes one peer membership per user.
- **Two comment paths.** Peer advisors comment through `/api/peer_advising/note/*_comment`; managers and advisors use `/api/note/*_comment`. Peer search reloads comments filtered by `peer_advising_department_id` (`Note.find_peer_notes_and_comments_by_ids`), so a comment stamped with `None` or another department's id won't come back with peer search results.
- **Topic usage joins on the topic string.** `get_peer_advising_note_topic_usage` matches `note_topics.topic` to `peer_advising_topics.topic`, so renaming a topic orphans its history.
- **Deleting a peer advisor deletes the user.** `delete_peer_advisor` soft-deletes the `authorized_users` row as well as the membership.
- **Restore is a GET that changes state** (`restore_peer_advisor`).
- **Enum name mismatch.** The model's ENUM is named `role_types` (`create_type=False`), while the DB type is `role_type_enum`. Keep this in mind when writing raw SQL.
- **Department migrations aren't safe to re-run.** They start with `DELETE ... WHERE name = ...`. Re-running one after notes exist fails on the `notes_peer_advising_department_id_fkey` FK, and the delete cascades to members.
- **Report totals don't agree.** `get_peer_advising_note_count_since` and `get_peer_advising_note_author_count` don't filter `is_draft`, and the author count includes PAM-authored notes. `get_total_peer_advising_notes` does filter drafts.
