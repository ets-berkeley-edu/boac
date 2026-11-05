# Advising notes and search

BOA shows a student's advising history (notes, appointments, eForms) on a timeline and lets advisors search it. Notes written in BOA live in the `boac` database. Notes, appointments, and eForms from other systems are read-only and come from the data loch. **Search never queries the `boac` database. It runs only against the data loch.** BOA-authored rows get into the loch through SQS change messages.

## Note sources

| Source | Where it lives | Read via |
|--------|----------------|----------|
| BOA-authored notes (incl. peer advising notes and note comments) | `boac.notes` (`boac/models/note.py`, `Note`) | `get_native_boa_notes()` in `boac/merged/advising_note.py` |
| SIS notes | loch `sis_advising_notes` schema | `get_sis_advising_notes()` → `data_loch.get_sis_advising_notes()` |
| ASC, Data Science, E&I, EOP, History Dept notes | loch `boac_advising_asc`, `boac_advising_data_science`, `boac_advising_e_i`, `boac_advising_eop`, `boac_advising_history_dept` (see `fixtures/loch/loch.sql`) | `get_asc_advising_notes()`, `get_data_science_advising_notes()`, `get_e_i_advising_notes()`, `get_eop_advising_notes()`, `get_history_dept_advising_notes()` |
| SIS eForms (late drop, career program plan, reduced course load) | loch `sis_advising_notes.student_{late_drop,cpp_change,course_load}_eforms` | `get_sis_late_drop_eforms()` etc. in `advising_note.py` |
| Appointments (SIS, Calendly, YCBM) | loch `sis_advising_notes.advising_appointments`, `boac_advising_appointments.*` | `get_advising_appointments()` in `boac/merged/advising_appointment.py` |

`get_advising_notes(sid)` in `boac/merged/advising_note.py` merges every note source *and the three eForm types* into a single `notes_by_id` dict. All of them go through `note_to_compatible_json()`, so the frontend gets one shape. eForms carry an `eForm` key and `legacySource: 'SIS'`. E&I and EOP notes are stamped with `dept_code = ['ZCEEE']`.

Read state comes from `NoteRead` (`boac/models/note_read.py`, table `notes_read`). Its `note_id` is a **string** column, so one table holds both integer BOA ids and string loch ids. Appointments use `AppointmentRead` (`appointments_read`) the same way.

The student timeline is assembled in `put_notifications(student)` in `boac/api/util.py`, called from `boac/api/student_controller.py`. That function:

- splits the notes into `note` and `eForm` buckets
- nests notes that have a `parentNoteId` under their parent's `comments`
- attaches appointment and eForm comments through `_attach_external_comments()`

## BOA note tables (`boac` DB)

- `notes` (`Note`): key columns are `author_uid/name/role/dept_codes`, `subject`, `body`, `contact_type` (enum `note_contact_types`), `is_draft`, `is_private`, `set_date`, `sid`, `note_template_id`, `parent_note_id`, `peer_advising_department_id`, `deleted_at`. All deletes are soft (`deleted_at`).
- `note_topics` (`boac/models/note_topic.py`): stores the topic as a free string (`String(50)`), not as a foreign key to `topics`.
- `topics` (`boac/models/topic.py`) and `peer_advising_topics` (`boac/models/peer_advising_topic.py`): the curated pick-lists, managed by `boac/api/topic_controller.py`.
- `note_attachments` (`boac/models/note_attachment.py`): one row per attachment, holding `path_to_attachment` (an S3 key).
- `note_templates`, `note_template_topics`, `note_template_attachments` (`boac/models/note_template*.py`, `boac/api/note_templates_controller.py`): templates belong to their creator (`creator_id`) or to a peer advising department.
- `notes_read` (`NoteRead`).

### Lifecycle (`boac/api/notes_controller.py`)

1. `POST /api/note/create_draft` (`create_draft_note`) calls `Note.create(is_draft=True, subject='')`. Admins and users with no advising department get a 403.
2. Autosave and edits go to `POST /api/notes/update` (`update_note`). A note is **published** when `isDraft` changes from true to false.
   - If it has more than one recipient SID (resolved from `sids`, `cohortIds`, and `curatedGroupIds` by `_get_sids_for_note_creation()`), `Note.create_batch()` inserts one row per SID with `json_populate_recordset` in chunks of 10000, and the draft is deleted.
   - Otherwise `Note.update()` publishes in place.
   - A published note can never go back to draft (400).
3. `DELETE /api/notes/delete/<id>` calls `Note.delete()`, which soft-deletes the note plus its attachments, topics, and child comment-notes.
4. `POST /api/note/apply_template` (`apply_template`) replaces the subject, body, topics, and attachments with the template's.

The "new note" flow has no create endpoint. It always starts as a draft. Peer advising notes are the exception: they are created directly, non-draft, by `POST /api/peer_advising/note/create` in `boac/api/peer_advising_notes_controller.py`.

### Drafts, privacy, and visibility

- **Drafts:** `_validate_sid()` in `note.py` allows a missing SID only while `is_draft`. Only the author can see a draft (`can_current_user_access_note()` in `advising_note.py`). Admins get every user's drafts from `GET /api/notes/my_drafts` (`Note.get_draft_notes(None)`). Drafts are never sent to SQS, so they never appear in search.
- **Private notes:** a user can read a private note's body and attachments only if `current_user.can_access_private_notes` is true. That flag is `canAccessPrivateNotes` in `boac/merged/user_session.py`, set for admins and CE3 (ZCEEE department) members. If the flag is false, `note_to_compatible_json()` returns `body = None` and `attachments = None`, and `download_attachment()` returns a 404. Only those same users can change `isPrivate` (`update_note`, 403 otherwise).
- **Peer advisors:** for a peer advisor, `can_current_user_access_note()` only returns true when the note has a `peer_advising_department_id` and the user holds the `peer_advisor` role there. Otherwise it returns `None`, so peer advisors cannot see regular advising notes. Editing is decided by `can_current_user_edit_note()`: the author, a peer advisor manager of the note's department, or the peer-advisor author.

## Comments: two separate systems

1. **Comments on BOA notes** are rows in `notes` with `parent_note_id` set.
   - Endpoints: `/api/note/add_comment`, `/api/note/edit_comment`, `/api/note/delete_comment/<id>` (admin only), plus the `/api/peer_advising/note/*_comment` equivalents.
   - Helpers: `create_note_comment()` and `update_note_comment()` in `boac/api/util.py`.
   - A comment inherits its parent's `is_private` and `sid`, and is stored with an empty `subject`.
2. **Comments on appointments and eForms** live in their own tables:
   - `comment_parents` (`boac/models/comment_parent.py`): `parent_type` is an enum (`appointment`, `course_load_eform`, `cpp_change_eform`, `late_drop_eform`) and `parent_id` is the loch's **string** id.
   - `comments` (`boac/models/comment.py`), `comment_attachments` (`comment_attachment.py`), and `comments_read` (`comment_read.py`).
   - Endpoints in `boac/api/comments_controller.py`: `POST /api/comments/create` (calls `CommentParent.find_or_create`), `POST /api/comments/update` (author only), `DELETE /api/comments/delete/<id>` (admin only).
   - Read state is handled by `record_external_comment_read_state()` and `mark_comments_read_for_parent()` in `boac/api/util.py`.

## Search architecture

### Write path: SQS change messages

`send(table, operation, rows)` in `boac/externals/sqs.py` posts one message per row to `AWS_SQS_QUEUE_URL`. The body is `{table, operation, row}`. `MessageGroupId` is `row['note_id']` for `note_topics` and `row['id']` for everything else. If the queue URL is unset, `send()` does nothing. Callers:

| Table | Operation | Sent from |
|-------|-----------|-----------|
| `notes` | `create` | `_create_notes()` (all non-draft creates) and `Note.update()` when publishing a draft |
| `notes` | `update` | `Note.update()` (non-draft), `Note.update_subject()` |
| `notes` | `delete` | `Note.delete()` (non-draft) |
| `note_topics` | `create` / `update` | `_add_topics_to_notes()`, `Note._update_note_topics()`. When a draft is published, its existing topics are queued as `create` |
| `comments` | `create` / `update` / `delete` | `Comment.create()`, `Comment.update()`, `Comment.soft_delete()` |

`Comment.to_sqs_json()` sends `comment_parent_id` set to the **loch parent id** (`CommentParent.parent_id`), not the `comment_parents` row id, and adds `parent_type`.

The consumer (the "CDC handler") is not in this repo. Based on the fixture DDL in `fixtures/loch/loch.sql`, it maintains these tables in the loch schema named by `DATA_LOCH_BOA_CDC_SCHEMA` (default `boa_app_rds_data`):

- `advising_notes`, with `id` like `'boa-<n>'` and `boa_id` the integer note id (inferred)
- `advising_notes_search_index`, with columns `raw_text`, `fts_index`, and `age_days`
- `advising_note_topics`
- `advising_note_authors_index`
- `advising_appointment_comments` and its `_search_index`
- `eform_comments` and its `_search_index`

BOA keeps no search index of its own. There's no materialized view, background reindex job, or reindex endpoint; search reads only the loch tables above.

### Read path

`POST /api/search` (`search()` in `boac/api/search_controller.py`, `@advisor_required`) handles the student, course, note, appointment, and eForm search domains:

- **Notes:** `_notes_search()` → `search_advising_notes()` (`boac/merged/advising_search.py`) → `data_loch.search_advising_notes()`. This runs a UNION of BOA CDC notes and legacy `boac_advising_notes.advising_notes`, each joined to its `advising_notes_search_index`. Rank = exact `ILIKE` bonus (10) + `phraseto_tsquery` bonus (5) + `ts_rank_cd(websearch_to_tsquery)`, multiplied by a recency decay (half-life 365 days, weight 0.8).
  - Filters: `topic`, advisor (`advisorUid`/`advisorCsid`, or `departmentCodes` resolved to UIDs from `boac` dept tables), `studentCsid`, and dates.
  - Results with an id starting `boa-` are parsed as local notes in `_parse_note_search_results()`.
- **Appointments:** `_appointments_search()` → `advising_appointment.search_advising_appointments()` → `data_loch.search_advising_appointments()`. This is a UNION of `boa_app_rds_data.advising_appointment_comments` with the loch `advising_appointments` and their search indexes. Appointments are skipped when a top-level `departmentCodes` param is present.
- **eForms:** `_eform_search()` → `advising_eform.search_advising_eforms()` → `data_loch.search_eforms()`. This is a UNION of `eform_comments` with `sis_advising_notes.student_eforms`. Results have `kind` set to `eform` or `commentOnEform`.
- All three go through `data_loch.search_advising()`, which runs a COUNT query first (and skips the page query when the count is 0), then a paged `candidates`/`page` CTE. `limit` is capped at 150.
- **Peer advising search:** `POST /api/search/peer_advising_notes` → `search_advising_notes(peer_advising_department_id=...)` → `data_loch.search_peer_advising_notes()`. It returns note ids, then reloads the full ORM `Note` objects and their comments from the `boac` DB with `Note.find_peer_notes_and_comments_by_ids()`, because the frontend edits them directly.
- **Advisor autocomplete:** `GET /api/search/advisors/find_by_name` → `match_local_note_authors_by_name()` (CDC `advising_note_authors_index`), plus legacy note authors and appointment advisors.
- **Snippets:** `search_result_text_snippet()` in `boac/lib/util.py` uses stemmed matches and `NOTES_SEARCH_RESULT_SNIPPET_PADDING`.

## Attachments

- **Upload:** `put_attachment_to_s3()` in `boac/lib/util.py` writes to bucket `DATA_LOCH_S3_ADVISING_NOTE_BUCKET` under `DATA_LOCH_S3_BOA_NOTE_ATTACHMENTS_PATH/YYYY/MM/DD/YYYYMMDD_HHMMSS_<filename>`. `get_attachment_filename()` strips that timestamp prefix for display.
- **Download:** `GET /api/notes/attachment/<id>` (`download_attachment`) streams the file through `s3.stream_object()`. Non-integer ids are legacy SIS or EOP attachments (`_get_legacy_attachment_stream`).
- **Allowed types:** an *allowlist*, not an exclude list. It is `NOTES_ATTACHMENTS_ALLOWED_TYPES` in `config/default.py`, grouped by label (documents, txt/csv, images, eml).
  - The server checks it in `get_note_attachments_from_http_post()` (`boac/api/util.py`) and returns 400 when a file has no extension or a disallowed one.
  - The list is exposed to the frontend as `allowedAttachmentTypes` (`boac/api/config_controller.py`) and checked there by `isAllowedAttachmentType()` in `src/lib/note.ts`.
- **Limit:** at most `NOTES_ATTACHMENTS_MAX_PER_NOTE` (10) attachments per note.

## Frontend

| Location | Role |
|----------|------|
| `src/api/notes.ts`, `peer-advising-notes.ts`, `comments.ts`, `note-templates.ts`, `topics.ts`, `appointments.ts`, `search.ts` | API clients |
| `src/stores/note-edit-session/index.ts` (`useNoteStore`) | Create/edit modal state: `mode` (one of `VALID_MODES`: `createBatch`, `createNote`, `editDraft`, ...), `model`, `recipients`, `autoSaveJob` |
| `src/stores/note-edit-session/note-edit-session-utils.ts` | `scheduleAutoSaveJob()` (interval from `config.notesDraftAutoSaveInterval`), `updateAdvisingNote()`, `exitSession()` |
| `src/components/note/` | `EditAdvisingNote.vue`, `AdvisingNote.vue`, `AdvisingNoteAttachments.vue`, `PrivacyPermissions.vue`, `BatchNote*.vue`, `eform/`, `template/` |
| `src/components/comment/AdvisingComments.vue` | Appointment and eForm comments |
| `src/components/search/` | `AdvancedSearch*.vue`, `AdvisingNoteSnippet.vue`, `AppointmentSnippet.vue`, `EformSnippet.vue`, `CommentSnippet.vue` |
| `src/views/SearchResults.vue`, `DraftNotes.vue`, `PeerAdvisorSearch.vue` | Pages |
| `src/components/student/profile/academic-timeline/` | Student timeline |

## Gotchas

- **Search reads only the loch.** A note saved in BOA is searchable only after the CDC consumer processes its SQS message. In tests, `fake_aws` in `tests/conftest.py` provides a moto queue but no consumer, so seed the loch yourself with `refresh_loch_note_search_index()`, `refresh_loch_appointment_search_index()`, or `refresh_loch_eform_search_index()` in `tests/util.py`.
- **Every write path must call `sqs.send`.** If you add a code path that changes a published note, topic, or comment and skip `sqs.send`, the search index silently drifts. Attachment changes are not queued at all.
- **"Comment" means two things.** On a note it is a `notes` row with `parent_note_id`. On an appointment or eForm it is a row in `comments`/`comment_parents`. Read state is split the same way (`notes_read` vs `comments_read`).
- **Private notes never appear in general note search.** `data_loch.search_advising_notes()` filters `NOT a.is_private`, even for CE3 users. Peer advising search has no such filter.
- **Date filters:** `UCBCONVERSION` legacy rows are filtered on `created_at`; everything else on `updated_at`.
- **`parse_search_phrases()` returns terms from a set,** so term order is not stable.
- **Template and batch notes share S3 objects.** They reuse the same S3 key across many `note_attachments` rows. Attachment deletes are soft only, so never delete the S3 object.
