# Course page

The course page (`/course/:termId/:sectionId`, `src/views/Course.vue`) shows one SIS class section in one term: a header with the course name, units, meetings, and instructors, then a paged table of the students in BOA's student population who are enrolled in it, with their bCourses (Canvas) analytics and midterm and final grades. Everything comes from the data loch except alert counts. Key files: `boac/api/course_controller.py`, `boac/merged/sis_sections.py` (`get_sis_section`), `boac/merged/student.py` (`get_course_student_profiles`), `boac/externals/data_loch.py`, `src/components/course/CourseStudents.vue`.

"Section ID" means the SIS class number (`ccn` in enrollment JSON, `sis_section_id` in the loch). Term IDs are 4-digit SIS term IDs (`<term_id>`).

## API (`boac/api/course_controller.py`)

| Method | Route | Decorator | Returns |
|---|---|---|---|
| GET | `/api/section/<term_id>/<section_id>?offset=&limit=&featured=` | `@advisor_required` plus an inline `current_user.can_access_canvas_data` check | The section (below) merged with `{students, totalStudentCount, meanMetrics}`. 403 `'Unauthorized to view course data'` without Canvas access; 404 if the section has no loch rows |

- This is the only course endpoint. `get_section` reads `offset` and `limit` with `int()` and passes `featured` (a UID) through as a string.
- See `.claude/docs/permissions.md` for `@advisor_required` and the `can_access_canvas_data` flag. Peer advisors never have Canvas access, so they can't use this page.
- There's no department scoping. Any advisor, director, or admin with Canvas access sees every enrolled student in the BOA population.

## Section header (`boac/merged/sis_sections.py`)

`get_sis_section(term_id, section_id)` → `data_loch.get_sis_section` reads `sis_data.sis_sections` (`DATA_LOCH_SIS_SCHEMA`). One section can have several rows, one per meeting/instructor combination, ordered by days, times, and instructor name.

- Returns `None` if the query fails and `False` if there are no rows. The controller turns either into a 404.
- Fields: `termId`, `termName` (`term_name_for_sis_id`), `sectionId`, `displayName` (`sis_course_name`), `title`, `instructionFormat`, `sectionNum`, `units`, `meetings`.
- `_maximum_units`: `allowed_units`, except `None` for `EAP` courses with more than 20 units (placeholder values). The page shows "Unknown Units" for `None`.
- `_get_meetings`: rows are grouped by an identical meeting dict (days, mode, location, dates, time), and instructor names are collected per meeting. Days become a full name for one day, or comma-separated three-letter names (`_days_in_friendly_format`). Times become `h:mm am - h:mm pm` and are dropped when start equals end. `instructionMode` codes map to names (`EF` Flexible, `EH` Hybrid, `ER` Remote, `P` In-person, `W` Online).
- `is_primary` is selected but not returned or checked, so the endpoint serves secondary sections too.

## Enrolled students (`boac/merged/student.py:get_course_student_profiles`)

```
data_loch.get_sis_section_enrollments(term, section, offset, limit)   # student.student_profile_index JOIN sis_data.sis_enrollments ON uid = ldap_uid
  → get_sis_section_enrollments_count(...)        # only if offset is set or the page is full (limit defaults to 50)
  → get_sis_section_enrollment_for_uid(featured)  # only if the featured UID isn't on this page; its SID is prepended
  → get_full_student_profiles(sids)               # student.student_profiles + photos + ASC/COE merges
  → data_loch.get_enrollments_for_term(term, sids)   # student.student_enrollment_terms.enrollment_term JSON
  → analytics.mean_metrics_across_sites(...)      # boac/lib/analytics.py
  → data_loch.get_sis_section_mean_gpas(term, section)   # boac_analytics.section_mean_gpas
```

- **Who is listed:** only students in `student_profile_index` (BOA's population) whose UID matches an `ldap_uid` in `sis_enrollments` for that term and section. Rows are sorted by last name, first name, then SID (natural ordering via `_naturalize_order`). Students without a `student_profiles` row are dropped silently.
- **Per-student fields.** `sisProfile` is removed and replaced by `academicCareerStatus`, `cumulativeGPA`, `cumulativeUnits`, `degrees`, `level` (`None` for `'Not Set'`), `majors` (sorted active plan descriptions), and `transfer`. Name, `sid`, `uid`, `photoUrl`, and the ASC/COE profile data stay as `get_full_student_profiles` returns them (see `.claude/docs/student-profile.md`, "What's hidden by role").
- **`enrollment`:** taken from the course in the term JSON whose `sections` include this `ccn`: `{canvasSites, enrollmentStatus (of the section), grade, gradingBasis, midtermGrade}`. Each `canvasSites[].analytics` has `assignmentsSubmitted`, `currentScore`, and `lastActivity`, with `student`, `courseDeciles`, and `boxPlottable` as built by the loch.
- **`analytics`** (per student) is the mean of the student's percentiles across the section's Canvas sites. **`meanMetrics`** is the same for `courseMean` across every distinct site seen, plus `gpa: {<gpa_term_id>: avg_gpa}`. `Course.vue` and `CourseStudents.vue` don't read either.
- **`alertCount`:** `_include_alert_counts` calls `Alert.current_alert_counts_for_sids(viewer_id, sids)`. It counts the viewer's undismissed alerts for the **current** term, for any course, not just this section. Students with none get `0`. `CourseStudents.vue` doesn't display it. See `.claude/docs/alerts.md`.
- **`totalStudentCount`:** `COUNT(DISTINCT sid)` from the same join, or the page length when the first page isn't full.

## Caching

None. Nothing on this path is stowed; every request runs the loch queries above and signs new photo URLs. `current_term_id()` (used for alert counts) is the only cached lookup.

## How users reach the page

| From | Link | Gate |
|---|---|---|
| Student page class list (`StudentCourse.vue`) | `/course/<termId>/<ccn>?u=<uid>` | `section.isViewableOnCoursePage`, set in `Student.vue` to `section.primary && currentUser.canAccessCanvasData` |
| Search results, course results (`SortableCourses.vue` in `SearchResults.vue`) | `/course/<termId>/<sectionId>` | Course search needs `can_access_canvas_data` (`search_controller`) and only returns primary sections (`sis_data.enrolled_primary_sections`) |

The router entry (`src/router.ts`, name `Course`) is a child of the `StandardLayout` route, whose guard allows advisors, directors, and admins. It has no Canvas check of its own; the API's 403 covers that.

## Frontend

| File | Role |
|---|---|
| `src/api/course.ts` | `getSection(termId, sectionId, offset, limit, featured)`. Sends `offset` and `limit` (default 50) when either is set, and `featured` when given |
| `src/views/Course.vue` | Reads route params and query `u` (featured UID), `p` (page, default 1), `s` (per page, 50 or 100). Renders the header, `CuratedGroupSelector` (more than one student), top and bottom `Pagination`, and the 50/100 per-page toggle (shown when the total exceeds 50). Moves the featured student to the top, gives students without `enrollment` a placeholder `{canvasSites: []}`, calls `setPageTitle(displayName)` and `ga.course('view', ...)`. Paging pushes `p` with `updateWindowLocationParam` and reloads |
| `src/components/course/CourseStudents.vue` | The student table (`v-data-table`, all rows of the current page). Columns: select/avatar, student details, Course Site(s), Assignments Submitted, Assignment Grades, bCourses Activity, Mid, Final |
| `StudentBoxplot.vue` (`src/components/student/`) | Highcharts boxplot used when a metric is `boxPlottable`; otherwise the raw score and max are shown as text |

Column details in `CourseStudents.vue`:

- **bCourses Activity** appears only when `section.termId` equals `config.currentEnrollmentTermId`. It shows `lastActivityDays(analytics)` per site (`src/lib/berkeley-utils.ts`).
- **Mid / Final** render through `v-accessible-grade` (`src/main.ts`), which swaps `+`/`-` for `&plus;`/`&minus;`. `isAlertGrade()` (grades starting with D, F, I, N, or R) adds a warning icon, hidden in demo mode. Without a final grade, the cell shows `gradingBasis`.
- **Details** show WAITLISTED (`enrollmentStatus === 'W'`), INACTIVE, the graduated icon, ASC/CoE inactive labels (`displayAsAscInactive`, `displayAsCoeInactive` in `src/lib/student.ts`), level and majors, or `DegreesAwarded` for completed students, plus team names from `athleticsProfile`.
- The featured row gets `list-group-item-info` and its name link `text-tertiary`. Names link with `studentRoutePath(uid, inDemoMode)`.
- Below a 1070px width the table switches to the `stacked-table` layout and hides the header row visually.

**Accessibility patterns to keep:**

- One `<h1 id="page-header">` (course name). "Details", "Schedule", and "Students" are `sr-only` `<h2>`s, and each student name is an `<h3>` inside its link.
- Skip links: "Skip to students" (`#course-students`) always, and "Skip to pagination" when there's more than one page. Both are `sr-only sr-only-focusable`.
- The table gets an `sr-only` `<caption>` "Course students: <displayName>" from the `v-table-caption` directive (`src/directives/tableCaption.ts`). Abbreviated headers ("Mid", "Final", "Course Site(s)") are `aria-hidden` with `sr-only` full text from the column's `ariaLabel`.
- Each boxplot is followed by an `sr-only` summary (score, max, 70th/50th/30th percentiles, min). With several Canvas sites, each value is prefixed by an `sr-only` course code. Empty cells use an em dash with `sr-only` "No data".
- The per-page toggle is a `role="group"` with `aria-label` and `aria-describedby`. Each button has `aria-pressed` and an `aria-label` ("Showing/Show N students per page"), and focus returns to the chosen button after reload (`putFocusNextTick`).
- `ManageStudent` is `sr-only` until its row is hovered or receives focus (`focusin`), so keyboard users can still reach it.
- Demo mode: names, SIDs, grades, course codes, and header fields carry `demo-mode-blur`; avatars use `img-blur`. Keep these on any new personal field.

## Tests

- `tests/test_api/test_course_controller.py`: 401 anonymous, 403 without Canvas access (`user_factory(can_access_canvas_data=False)`), 404 for an unknown section, section header fields, per-student enrollment and Canvas analytics, mean metrics, ASC vs non-ASC athletics data, and `alertCount` with the `create_alerts` fixture. Paging and `featured` aren't covered.
- In tests, `get_sis_section` and `get_sis_section_enrollments` are `@fixture`-decorated and read `fixtures/loch/sis_section_<term>_<section>.csv` and `sis_section_enrollments_<term>_<section>.csv`. The count, featured-UID, term-enrollment, and mean-GPA queries run against `boac_loch_test` (`fixtures/loch/loch.sql`). Add both CSV and SQL data when adding a test section.

## Gotchas

- **Canvas access gates the whole page,** not just the Canvas columns. A user without `can_access_canvas_data` gets 403 even for grades and the roster, and the student page hides the link for them.
- **The roster is joined on UID, not SID.** A student whose `student_profile_index.uid` doesn't match `sis_enrollments.ldap_uid` won't appear.
- **`featured` is a UID** in both the `u` query param and the API. The backend adds the featured student's SID only if they're enrolled and not already on the page, so a page can come back with `limit + 1` students; `Course.vue` sorts the featured student first and slices to the page size.
- **`alertCount` is current-term and course-independent,** even on a past term's section.
- **`termId` arrives as a string.** Compare with `parseInt` on the frontend (as the bCourses-column check does) and keep loch params as strings.
- **No caching and several loch queries per page,** including the full profile JSON for every listed student. Keep page sizes small.
