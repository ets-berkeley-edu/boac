# CSV exports and other downloads

This doc covers every way student or user data leaves BOA as a file: the "Export List" CSV for cohorts, curated groups, and admits; the notes zip on the student page; and the admin, user-list, and peer advising CSVs. Key files: `boac/api/cohort_csv_controller.py`, `boac/api/csv_file_download_utils.py`, `boac/lib/http.py` (`response_with_csv_download`), `src/lib/berkeley-utils.ts` (column lists), and `src/components/util/ExportListModal.vue`.

Related docs: cohort filters and phantom cohorts are in `.claude/docs/cohorts.md`. Curated group view rules are in `.claude/docs/curated-groups.md`. Admit data and the CE3 checks are in `.claude/docs/admitted-students.md`. Note privacy and attachments are in `.claude/docs/notes-and-search.md`. Decorators are in `.claude/docs/permissions.md`. The admin and user-list pages are in `.claude/docs/admin-and-users.md`.

## Student list CSV endpoints

| Method | Route | Decorator | Inline checks |
|---|---|---|---|
| POST | `/api/cohort_csv/download` `{cohortId, csvColumnsSelected, termId}` (`download_cohort_csv`) | `@advisor_required` | `can_current_user_view_cohort(owner_uid)`: non-admins can't export an admin-owned cohort (404). Uses the saved `cohort_filters.sids` (`CohortFilter.get_sids`). Domain comes from the saved cohort |
| POST | `/api/cohort_csv/download_per_filters` `{filters, csvColumnsSelected, domain, termId}` (`download_csv_per_filters`) | `@advisor_required` | 400 if `filters` is missing (or empty in the `default` domain). `is_unauthorized_search(filter_keys)` → 403. `is_unauthorized_domain(domain)` → 404 (400 for an unknown domain). SIDs come from `construct_phantom_cohort(..., include_sids=True)` |
| POST | `/api/curated_group/<id>/download_csv` `{csvColumnsSelected, termId}` (`curated_group_controller.download_csv`) | `@advisor_required` | 404 if the group doesn't exist. `_can_current_user_view_curated_group()` → 403. Exports every SID in the group (`CuratedGroup.get_all_sids`) |

- **Size cap.** Both cohort endpoints raise 400 when the SID count exceeds `COHORT_CSV_MAXIMUM_POPULATION` (`config/default.py`, 10000). The curated group endpoint has no cap.
- **`termId`** defaults to `current_term_id()`. It only affects `units_in_progress` (`get_term_units_by_sid`) and `course_activity` (`data_loch.get_enrollments_for_term`).
- **`csvColumnsSelected`** is a list of column keys. The backend doesn't validate it against the UI list: an unknown key in the default domain becomes an empty column, and in the admit domain any column returned by `get_admitted_students_by_sids` can be requested.
- All three endpoints hand off to `response_with_students_csv_download(benchmark, domain, fieldnames, sids, term_id)`. It sends `admitted_students` to `_response_with_admits_csv_download` and everything else to `_response_with_students_csv_download`.

## Default-domain columns (`_response_with_students_csv_download`)

Rows come from `data_loch.get_student_profiles(sids)` (the `student_profiles.profile` JSON), plus `get_term_gpas_by_sid` and `get_term_units_by_sid`. Each column has a getter in the `getters` dict and a header label in `get_students_csv_header_labels()`. The UI list is `getDefaultCsvExportColumns()` in `src/lib/berkeley-utils.ts`, and the default selection is `first_name, last_name, sid, email, phone` (`getCsvExportColumnsSelected`).

| Key(s) | Source |
|---|---|
| `first_name`, `last_name`, `sid` | Top-level `firstName`, `lastName`, `sid` |
| `email`, `phone`, `entering_term`, `terms_in_attendance`, `cumulative_gpa`, `units_completed` | `sisProfile.emailAddress`, `phoneNumber`, `matriculation`, `termsInAttendance`, `cumulativeGPA`, `cumulativeUnits` |
| `majors`, `subplans`, `college` | `sisProfile.plans` with `status == 'Active'`: `description`, `subplan`, distinct `program` |
| `minors` | Active `sisProfile.plansMinor` descriptions |
| `program_status` | Distinct `status` values across all `sisProfile.plans` |
| `level_by_units`, `expected_graduation_term`, `transfer` | `sisProfile.level.description`, `expectedGraduationTerm.name`, and `'Yes'` or blank from `transfer` |
| `intended_major` | `sisProfile.intendedMajors[].description`. The backend also has `intended_majors`, which the UI doesn't offer |
| `term_gpa_<termId>` (two columns) | `get_term_gpas_by_sid` for the two terms before the **current** term, whatever `termId` is |
| `units_in_progress` | `get_term_units_by_sid(term_id)`, defaulting to `'0'` |
| `academic_standing`, `college_advisor` | `get_academic_standing(profile)` and `get_college_advisors(profile)` in `boac/api/util.py` |
| `coe_status` | `get_coe_status()` after `merge_coe_student_profile_data`. The getter exists only for admins and users advising in `COENG`; the UI offers it to `isAdmin \|\| isCoe` |
| `cohorts`, `curated_groups` | Names of the **current user's** cohorts (`CohortFilter.get_cohorts(user_id)`) and owned groups that contain the SID. The UI disables them when the user has no `default`-domain cohorts or groups |
| `course_activity` | Not a column itself. It's removed from `fieldnames` and adds `Class Name` (with ` (waitlisted)` when a section has status `W`), `Units`, `Mid-point Grade`, and `Final Grade` (grade, else grading basis). It produces **one row per enrollment**, repeating the student columns |

Multi-value cells are joined with `'; '`. Rows are sorted by upper-cased last name, first name, then SID (`_norm`). The filename prefix is `cohort` for all three endpoints.

## Admit-domain columns (`_response_with_admits_csv_download`)

- The helper is decorated with `@ce3_required`, so a non-CE3 caller who gets this far gets a 401.
- Rows come from `data_loch.get_admitted_students_by_sids(offset=0, sids=sids)`. Each requested key is read straight from the row, except `cs_empl_id`, which is read from the `sid` alias.
- The UI list is `getAdmitCsvExportColumns()`: names, IDs, birthdate, permanent address, ethnicity, citizenship and visa, parent education, GPAs, income, dependents, and program flags. There's no column picker for admits: the UI always sends every column (see Frontend).
- No header label lookup is passed, so the header row is the raw keys. Rows sort by last name, first name, `cs_empl_id`.

## Other downloads

| Route | Decorator | Contains |
|---|---|---|
| `GET /api/notes/<sid>/download?type=note\|eForm` (`notes_controller.download_notes`) | `@director_advising_data_access_required` | A streamed zip (`get_zip_stream`, `boac/merged/advising_note.py`, built with `zipstream`). It holds `advising_<type>s_<first>_<last>_<YYYYMMDD>.csv` with `date_created, student_sid, student_name, author_uid, author_csid, author_name, subject, body, topics, attachments, is_private`, plus each attachment's file. Notes come from `get_advising_notes(exclude_draft_notes=True)`. `type=eForm` keeps only eForms; any other value keeps only non-eForm notes. Private-note bodies and attachments are left out unless `can_access_private_notes`. Duplicate attachment names get ` (1)`, ` (2)` suffixes. 404 if the student is unknown or has no notes |
| `GET /api/reports/boa_notes/metadata` (`admin_reports_controller.get_boa_notes_metadata`) | `@admin_required` | `boa_advising_notes_metadata_<ts>.csv`: every non-draft, top-level BOA note's metadata (no body) plus student name, degrees, and the names of **all users'** cohorts and curated groups containing the SID (`get_summary_of_boa_notes`) |
| `POST /api/peer_advising/<id>/notes/csv` (`peer_advising_reports_controller`) | `@peer_advisor_manager_in_department` | `boa_peer_advising_notes_<ts>.csv`: the department's non-draft top-level notes with author, **body** (newlines collapsed to spaces), topics, and student name and email (`get_all_peer_advising_notes`), newest first |
| `POST /api/users` with `isCsvDownloadRequest` | `@admin_required` | `boa-users_<ts>.csv`. Columns are the keys of the last `authorized_users_api_feed` entry (CalNet fields plus BOA flags), headers from `_get_inputs_for_csv_download`. Rows re-sorted by last name |
| `POST /api/users/admins`, `POST /api/users/peer_advising` with `isCsvDownloadRequest` | `@admin_required` | `boa-admin-users_<ts>.csv` and `peer-advising-users_<ts>.csv`, built the same way. The UI doesn't request either as CSV |
| `GET /api/notes/attachment/<id>`, `GET /api/appointments/attachment/<id>`, `GET /api/peer_advisor/note/attachment/<id>` | `@advising_data_access_required` (first two), `@peer_advisor_or_peer_advisor_manager` | One attachment streamed from S3 as `application/octet-stream` with `filename*=UTF-8''…`. See `.claude/docs/notes-and-search.md` and `.claude/docs/peer-advising.md` |

Degree checks have no server-side file. "Print" opens the `/degree/:id/print` route (`PrintableDegreeTemplate.vue`) for the browser's print dialog.

## How the files are built

- `response_with_csv_download(rows, filename_prefix, fieldnames, header_label_lookup=None)` (`boac/lib/http.py`) writes with `csv.DictWriter` into a `werkzeug` `ResponseStream`. The response is `content_type='text/csv'` with no charset; the body is UTF-8 with no BOM. The header row uses `header_label_lookup` (falling back to the key) or `writeheader()`.
- The server sets `Content-disposition: attachment; filename="<prefix>_<YYYY-MM-DD_HH-MM-SS>.csv"`, but the axios-based exports ignore it. The client names the file with `utils.createDownloadFilename(prefix, 'csv')` (`src/api/api-utils.ts`), which strips everything but letters, digits, spaces, and hyphens, and saves it with `js-file-download`.
- The notes zip writes its CSV with `csv.writer` one line at a time. Its `Content-Disposition` is `attachment; filename=<url-quoted name>.zip`.
- No values are escaped for spreadsheet formulas.

**Logging and tracking.** BOA keeps no audit record of exports. The backend only writes `get_benchmarker` timings at debug level. In the browser, `downloadCohortCsv`, `downloadCsv` (`src/api/cohort-csv.ts`), and `downloadCuratedGroupCsv` (`src/api/curated.ts`) send a GA `download` event in the `Cohort` category whose label is the file name or `Curated group: <name>`. `ga.track` skips admins. The notes zip, admin, user, and peer CSVs send no GA event.

## Frontend

| File | Role |
|---|---|
| `src/api/cohort-csv.ts` | `downloadCohortCsv` (saved cohort) and `downloadCsv` (by filters). Both send `termId = currentUser.preferences.termId \|\| config.currentEnrollmentTermId` |
| `src/api/curated.ts`, `src/api/peer-advising-reports.ts`, `src/api/user.ts` | `downloadCuratedGroupCsv`; `downloadPeerAdvisingNotes`; `getUsers`/`getAdminUsers`/`getPeerAdvisingUsers`, which download when given a `csvFilenamePrefix` |
| `src/components/util/ExportListModal.vue` | "Export List" dialog: a checkbox per column in a `role="group"` labeled "Select columns to export.", the `FerpaReminder` text, an error `v-alert`, and Export / Cancel buttons |
| `src/components/util/FerpaReminderModal.vue` | "FERPA Reminder" dialog with "I understand" / Cancel. Used for admit exports instead of a column picker |
| `src/components/cohort/CohortPageHeader.vue` | "Export List" (`#export-student-list-button`), disabled while downloading, with no students, or with unapplied filter edits. A saved cohort viewed by a non-owner exports by `cohortId`; everything else exports by the current `filters` |
| `src/components/curated/CuratedGroupHeader.vue` | "Export List" for a curated group, through the same two modals |
| `src/views/AdmitStudents.vue` | "Export List" on `/admit/students`: `downloadCsv('admitted_students', 'CE3 Admissions', [], <all admit columns>)` after the FERPA dialog |
| `AcademicTimelineTable.vue` | "Download notes" link (`#download-notes-link`, a plain `href` to `/api/notes/<sid>/download?type=note`). Shown on the Notes tab only, to admins and directors, when a non-draft note exists |
| `src/components/reports/NotesReport.vue`, `PassengerManifest.vue`, `PeerAdvisorManagerReports.vue` | The metadata "download" link, the users "CSV download" button (all active users), and the peer "download notes" button |

**Accessibility patterns to keep (WCAG 2.2 AA):**

- Both dialogs use `FocusLock` with `@keydown.esc="cancel"`, `ModalHeader`, `persistent`, and `aria-labelledby="modal-header"` plus `aria-describedby`. `FerpaReminderModal` calls `toggleModalBackgroundDisabled` and focuses its confirm button. The headers call `putFocusNextTick('csv-column-options-0')` when the column picker opens.
- Announce each step with `alertScreenReader`: "Exporting …", "Downloading …", "Canceled export …", and failures. On cancel or finish, return focus to `export-student-list-button`.
- Use `ProgressButton` for the in-progress state, and disable the checkboxes and Cancel while exporting.
- `FerpaReminder.vue`'s external link says "(opens in new tab)" in its `aria-label`. `NotesReport.vue` adds `sr-only` " notes report" to its "download" link text.

## Tests

`tests/test_api/test_cohort_csv_controller.py` (`TestDownloadCohortCsv`, `TestDownloadCsvPerFilters`, including custom columns, the admit domain, and non-CE3 denial), the CSV case in `test_curated_group_controller.py`, `TestStreamNotesZip` in `test_notes_controller.py`, `TestBoaNotesMetadataReport` in `test_admin_reports_controller.py`, `TestPeerAdvisingDownloadCSV` in `test_peer_advising_reports_controller.py`, and `TestDownloadBoaUsersCSV` in `test_user_controller.py`. `TestDownloadBoaUsersCSV` posts `csvDownloadFilename`, not `isCsvDownloadRequest`, so it exercises the JSON path.

## Gotchas

- **Exports carry FERPA data.** Never put CSV rows, filenames (the notes zip name includes the student's name), or selected values into logs, fixtures, docs, or GA labels.
- **The saved-cohort export uses cached SIDs.** `download_cohort_csv` reads `cohort_filters.sids`, which can lag the live filter results; see the caching notes in `.claude/docs/cohorts.md`. Owners export by live filters instead.
- **Term columns are pinned to the current term.** `term_gpa_*` keys and labels always use `previous_term_id(current_term_id())`, even when `termId` points elsewhere.
- **`course_activity` changes the row shape.** One row per enrollment, and `_response_with_students_csv_download` mutates the `fieldnames` list it was given.
- **A column key needs three places:** the backend `getters` dict, `get_students_csv_header_labels()`, and `getDefaultCsvExportColumns()`. If one is missing, you get an empty column or a raw-key header.
- **Admit exports are all-or-nothing in the UI.** There's no column picker, so every admit column, including address, birthdate, and income, is downloaded.
- **Status codes differ by path.** Unauthorized admit export returns 404 through `download_per_filters`, 401 through the `@ce3_required` helper, and 403 through a curated group the user can't view.
