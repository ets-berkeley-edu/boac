# Student profile page

The student page (`/student/:uid`, `src/views/Student.vue`) shows one enrolled or former student: a header with bio and academic plans, unit and GPA totals, the academic timeline, and classes by term. The backend reads almost everything from the data loch, which stores most of it as pre-built JSON. BOA's own database adds only alerts, BOA-authored notes, read state, and degree checks. Key files: `boac/api/student_controller.py`, `boac/merged/student.py` (`_construct_student_profile`), `boac/api/util.py` (`put_notifications`), and `boac/externals/data_loch.py`.

Admitted (not yet enrolled) students have a separate page, `/admit/student/:sid`, behind `@ce3_required`. See `.claude/docs/admitted-students.md`.

## API (`boac/api/student_controller.py`)

| Method | Route | Decorator | Returns |
|---|---|---|---|
| GET | `/api/student/by_uid/<uid>` | `@advisor_required` | The full profile (below). This is what `Student.vue` calls |
| GET | `/api/student/by_sid/<sid>` | `@advisor_required` | The same profile, looked up by SID. Used by the degree-check views |
| POST | `/api/students/by_sids` `{sids}` | `@advisor_required` | `[{label, sid, uid}]`. 400 if any SID isn't numeric |
| POST | `/api/students/find_by_name_sid_or_email` `{query, limit, includeEmailAddressInLabel}` | `@advisor_or_peer_advisor_required` | Typeahead matches `[{label, sid, uid}]` (default limit 20) |
| POST | `/api/students/validate_sids` `{sids, domain}` | `@advisor_required` | `[{sid, status: 200 or 404}]`. 403 for an unauthorized domain |
| POST | `/api/students/distinct_sids` `{sids, cohortIds, curatedGroupIds}` | `@advisor_required` | `{sids}`. See `.claude/docs/curated-groups.md` |

- **`?profileOnly=true`** skips `put_notifications()` and the degree checks (`_decorate_student`). The degree views use it because they only need the header.
- **Not found:** if the loch has no row for the SID or UID, or no `student_profiles` JSON for it, `_decorate_student` raises `ResourceNotFoundError('Unknown student')` (404).
- **No department scoping.** Neither profile endpoint checks which department the student belongs to. Any advisor, director, or admin can load any student. What varies by viewer is which parts of the payload are filled in (see "What's hidden by role").

## How the profile is assembled (`boac/merged/student.py`)

```
get_student_and_terms_by_uid(uid) / get_student_and_terms_by_sid(sid)
  → data_loch.get_student_by_uid / get_student_by_sid      # student.student_profile_index
  → _construct_student_profile(student)
      → get_full_student_profiles([sid])                    # student.student_profiles.profile JSON
          → _merge_photo_urls()                             # signed S3 URLs
          → _merge_asc_student_profile_data(scope)          # boac_advising_asc.student_profiles
          → merge_coe_student_profile_data()                # boac_advising_coe.student_profiles (COENG/ADMIN scope only)
      → get_academic_standing_by_sid([sid])                 # student.academic_standing
      → data_loch.get_enrollments_for_sid(sid, latest_term_id=future_term_id())
      → merge_enrollment_terms(...)                         # student.student_enrollment_terms
  → _decorate_student(): put_notifications() + _put_degree_checks_json()   (skipped with profileOnly)
```

### Loch sources

Schema names come from config: `DATA_LOCH_STUDENT_SCHEMA` (`student`), `DATA_LOCH_ASC_SCHEMA` (`boac_advising_asc`), `DATA_LOCH_COE_SCHEMA` (`boac_advising_coe`). Table definitions for tests are in `fixtures/loch/loch.sql`.

| Part of the payload | Loch table | Function |
|---|---|---|
| Lookup row (`sid`, `uid`, `academic_career_status`, ...) | `student.student_profile_index` | `get_student_by_sid`, `get_student_by_uid` |
| Top-level `name`, `firstName`, `lastName`, `sid`, `uid`, `sisProfile` (plans, minors, `degrees`, `level`, `academicCareerStatus`, `academicStanding`, `cumulativeGPA`, `cumulativeUnits`, `withdrawalCancel`, `degreeProgress`, contact info), `demographics`, `advisors` | `student.student_profiles.profile` (JSON text) | `get_student_profiles` |
| `athleticsProfile` | `boac_advising_asc.student_profiles` | `get_athletics_profiles` |
| `coeProfile` | `boac_advising_coe.student_profiles` | `get_coe_profiles` |
| `enrollmentTerms[].academicStanding` | `student.academic_standing` | `get_academic_standing` → `get_academic_standing_by_sid` |
| `enrollmentTerms` (enrollments, sections, grades, `droppedSections`, `enrolledUnits`, `termGpa`, unit limits, `canvasSites[].analytics`) | `student.student_enrollment_terms.enrollment_term` (JSON text) | `get_enrollments_for_sid` |
| `notifications.hold` | `student.student_holds.feed` (JSON text) | `get_sis_holds` (called from `put_notifications`) |
| `photoUrl` | S3 `DATA_LOCH_S3_PHOTO_BUCKET` / `DATA_LOCH_S3_PHOTO_PATH/<uid>.jpg` | `s3.get_signed_urls`, expiring after `PHOTO_SIGNED_URL_EXPIRES_IN_SECONDS` (15 min) |

### Changes `_construct_student_profile` makes to the loch JSON

- `sisProfile.level.description` is set to `None` when the loch says `'Not Set'` (`_get_sis_level_description`).
- **Academic standing per term:** rows are reduced to `{termId: status}` (the last row per term in `action_date` order wins) and attached to every term as `academicStanding: {status, termId}`. `status` can be `None`.
- **COE standing:** when `coeProfile.acadStatusDescription` is set, the term whose `termId` equals `coeProfile.acadStatusTermId` gets `coeAcademicStanding: {description, status, termId}`. `merge_coe_student_profile_data` also sets `acadStatusDescription` (from `COE_ACADEMIC_STANDING_DESCRIPTIONS`), `underrepresented`, and `isActiveCoe` (false for statuses `D O P U W X Z`).
- **Withdrawal:** `sisProfile.withdrawalCancel` is also copied to top-level `withdrawalCancel`. If it has no `termId`, the current term ID is filled in (same object, so both copies change).
- **Advisors:** an advisor entry with `sid == 'UCBUGADHAAS'` is relabeled as the Haas Undergraduate Program with a generic Haas email.

### Terms (`merge_enrollment_terms`)

- Terms run from `LEGACY_EARLIEST_TERM` (`earliest_term_id()`, Fall 2001) through `future_term_id()` (`CANVAS_FUTURE_ENROLLMENT_TERM`), newest first.
- Past terms with no `enrollments` and no `droppedSections` are dropped. In past terms, waitlisted sections (`enrollmentStatus == 'W'`) are removed, unless that would leave a course with no sections (`_omit_zombie_waitlisted_enrollments`).
- **The current term is always present.** If the loch has no row for it, an empty term (`enrolledUnits: 0`, `enrollments: []`) is appended at the end of the list.
- Each term gets `academicYear` (`academic_year_for_term_name`).

### Notifications and degree checks

`put_notifications(student)` (`boac/api/util.py`) builds `student.notifications`, which feeds the timeline:

| Key | Source | Present when |
|---|---|---|
| `alert` | `Alert.current_alerts_for_sid` (see `.claude/docs/alerts.md`) | always |
| `hold` | `student_holds` feed; `read: True`, `createdAt = fromDate` | always |
| `requirement` | `sisProfile.degreeProgress.requirements`; `read: True` | always |
| `note`, `eForm`, `appointment` | see `.claude/docs/notes-and-search.md` | only if `current_user.can_access_advising_data` |

`_put_degree_checks_json` sets `degreeChecks` to `DegreeProgressTemplate.find_by_sid()` when `current_user.can_read_degree_progress`, otherwise `[]`. The student page doesn't read this field; the "Degree Checks" link loads its own data. See `.claude/docs/degree-progress.md`.

## Caching

Nothing on the profile path is stowed. Every page load queries the loch and BOA DB and signs a new photo URL. The only cached piece is the current-term lookup: `current_term_id()` / `future_term_id()` (`boac/merged/sis_terms.py`) use `@stow('current_term_index')` when `CANVAS_CURRENT_ENROLLMENT_TERM` / `CANVAS_FUTURE_ENROLLMENT_TERM` is `'auto'`.

## What's hidden by role

`get_student_query_scope()` returns `['ADMIN']` for admins and the viewer's advising dept codes otherwise (see `.claude/docs/permissions.md`).

| Data | Who gets it | Where enforced |
|---|---|---|
| Full `athleticsProfile` | `UWASC` or `ADMIN` scope | `_merge_asc_student_profile_data` |
| `athleticsProfile: {athletics}` only (team memberships) | other viewers, and only if `isActiveAsc` | same |
| `coeProfile`, `coeAcademicStanding` | `COENG` or `ADMIN` scope | `get_full_student_profiles` |
| `canvasSites` (emptied otherwise) | `can_access_canvas_data` | `merge_enrollment_terms` → `_suppress_canvas_sites` |
| Notes, eForms, appointments | `can_access_advising_data` | `put_notifications` |
| `degreeChecks` | `can_read_degree_progress` | `_put_degree_checks_json` |

The frontend adds display-only checks: "ASC INACTIVE" (`displayAsAscInactive`, UWASC advisors/directors), "CoE INACTIVE" and COE standing (`displayAsCoeInactive`, `displayCoeAcademicStanding`, admin or COENG) in `src/lib/student.ts`; the Degree Checks link (`canReadDegreeProgress`); the New Note button (`!isAdmin && canAccessAdvisingData`, `AcademicTimelineHeader.vue`); and course-page links (`section.primary && canAccessCanvasData`, set in `Student.vue`).

## Inactive, completed, and unknown students

- The profile endpoints don't filter on `academic_career_status`, so inactive and completed students load normally.
- `sisProfile.academicCareerStatus === 'Inactive'` shows a red "INACTIVE" label next to the SID. `'Completed'` shows a graduation-cap icon with a "Graduated" tooltip (`StudentProfileHeaderBio.vue`).
- For `'Completed'`, `StudentProfileHeaderAcademics.vue` lists `sisProfile.degrees` (with minors and award dates) instead of majors and minors. Otherwise it shows active plans, and falls back to discontinued majors, minors, and subplans when no plan is active.
- An unknown UID or SID returns 404. The axios interceptor (`src/lib/axios-utils.ts`) sends any 404 to `/404`. `Student.vue` has no `.catch` of its own.

## Frontend

| File | Role |
|---|---|
| `src/api/student.ts` | `getStudentByUid(uid, profileOnly?)`, `getStudentBySid`, `getStudentsBySids`, `validateSids`, `findStudentsByNameSidOrEmail`, `getDistinctSids`, `dismissStudentAlert` |
| `src/views/Student.vue` | Loads the student, sets the page title, adds `displayName`, `isViewableOnCoursePage`, and waitlist status to sections, and builds `termGpa` from each term's `termGpa`. Guards route-leave with `AreYouSureModal` while a note is being edited |
| `components/student/profile/StudentProfileHeader.vue` | Wraps `StudentProfileHeaderBio`, `StudentAvatar`, `ManageStudent` (curated groups), `StudentProfileHeaderAcademics`, `StudentPersonalDetails`. `compact` / `linkToStudentProfile` / `suppressGradPrograms` props are used by the degree views |
| `StudentProfileHeaderBio.vue` | `<h1 id="page-header">` with the name, SID, status labels, standing, email, level, terms in attendance, expected graduation, teams |
| `StudentPersonalDetails.vue` | Collapsible: advisors, alternate email, phone, transfer/matriculation/visa, CalCentral and Perceptive links, intended majors |
| `StudentProfileUnits.vue`, `StudentProfileGPA.vue` | `sisProfile.cumulativeUnits`, `sisProfile.cumulativeGPA`, term GPA table |
| `academic-timeline/` | Timeline of notifications (see `.claude/docs/notes-and-search.md`, `.claude/docs/alerts.md`) |
| `StudentClasses.vue` → `StudentEnrollmentTerm.vue` → `StudentCourse.vue` / `StudentCourseCanvasData.vue` | Terms grouped by academic year (`getEnrollmentTermsByYear`, `src/lib/student.ts`), with per-term standing, withdrawal, GPA, and unit limits |
| `src/components/student/StudentDegreeCheckLink.vue` | Opens degree checks via `goToStudentDegreeChecks(sid)` |

**Accessibility patterns to keep:**

- The page has one `<h1>` (the name). Sections are `role="region"` with `aria-labelledby` pointing at their `<h2>` (Academic Status is an `sr-only` heading). Years are `<h3>`, terms `<h4>`.
- Year toggles are `<button>`s with `aria-expanded`, `aria-controls`, and an `aria-label` that includes the unit total. "Expand/Collapse all years" and "Sort academic year" announce through `alertScreenReader`.
- The class list is a `role="table"` / `row` / `columnheader` / `cell` structure with `sr-only` text completing abbreviated headers ("Mid" and "Final" are followed by hidden "term grade" / "grade").
- "SID" is read as "S I D" (`sr-only` text plus an `aria-hidden` visual label). Links that open a new tab say so in `sr-only` text or `aria-label`.
- Demo mode blurs personal fields with `demo-mode-blur` / `img-blur`. Keep that class on any new personal field.

## Gotchas

- **The route uses UID, not SID.** `/student/:uid` calls `by_uid`. In demo mode the UID in the URL is base64-encoded: build links with `studentRoutePath(uid, inDemoMode)` (`src/lib/utils.ts`), because `Student.vue` decodes with `window.atob`.
- **One UID can match several index rows.** `get_student_by_uid` prefers the first row with a non-empty `academic_career_status`, otherwise the first row. `by_sid` is exact.
- **`termId` is a string.** Standing is matched by `term['termId'] == ...`, and `_academic_standing_to_feed` stringifies `term_id`. Keep IDs as strings when adding per-term data.
- **Two academic-standing sources.** The header shows `sisProfile.academicStanding` straight from the profile JSON; each term shows `term.academicStanding` from the `academic_standing` table. `StudentAcademicStanding.vue` hides status `GST`.
- **Withdrawal shows on terms by `termId` match.** `StudentWithdrawalCancel.vue` renders on the term whose ID equals `withdrawalCancel.termId`, and the backend defaults a missing one to the current term.
- **The empty current term is appended last,** not in date order. The frontend regroups terms by academic year, so it doesn't matter there, but other consumers of `enrollmentTerms` should not assume strict ordering.
- **Profile loads are uncached and heavy.** One request runs several loch queries plus all note and appointment sources. Use `profileOnly=true` when the timeline isn't needed.
- **Non-ASC viewers see team names only for active ASC students.** Don't add other `athleticsProfile` fields to shared components without checking scope.
