<template>
  <div class="student-table-wrapper">
    <slot v-if="!students?.length && !isFetching" name="noData" />
    <div v-if="!students?.length && isFetching" class="align-center d-flex pt-3">
      <slot name="loading">Loading students…</slot>
    </div>

    <table
      v-if="students?.length"
      id="student-curriculum-table"
      class="d-block mt-5 w-100"
    >
      <caption class="sr-only">
        Students list with expandable curriculum section. Use the expand button in the last column.
      </caption>

      <thead class="sr-only">
        <tr>
          <th scope="col">Student</th>
          <th scope="col">SID</th>
          <th scope="col">Email</th>
          <th scope="col">Major</th>
          <th scope="col">Expand</th>
        </tr>
      </thead>

      <tbody class="d-block w-100">
        <tr
          v-for="(student, index) in students"
          :id="`tr-student-${studentKey(student, index)}`"
          :key="studentKey(student, index)"
          :class="{
            'bg-alt': index % 2 === 0,
            'expanded border-b-sm': isExpanded(student),
            'border-b-md': index === students.length - 1
          }"
          tabindex="-1"
        >
          <!-- Student Name -->
          <td class="td-student">
            <div class="grid-cell">
              <span v-if="!sidsWithNotes.includes(student.sid)" class="font-weight-bold">
                {{ getStudentName(student) }}
              </span>
              <a
                v-if="sidsWithNotes.includes(student.sid)"
                class="font-weight-bold"
                :href="`search?q=${student.sid}&tab=note`"
              >
                {{ getStudentName(student) }}
              </a>
            </div>
          </td>

          <!-- SID -->
          <td class="td-sid">
            <div class="grid-cell">
              <span class="mono">{{ student.sid ?? '—' }}</span>
            </div>
          </td>

          <!-- Email -->
          <td class="td-email">
            <div class="grid-cell">
              <a
                v-if="getStudentEmail(student)"
                :href="`mailto:${getStudentEmail(student)}`"
              >
                {{ getStudentEmail(student) }}
              </a>
              <span v-else>—</span>
            </div>
          </td>

          <!-- Major -->
          <td class="td-major">
            <div class="grid-cell">
              <template v-if="getMajors(student).length">
                <v-tooltip location="top">
                  <template #activator="{ props }">
                    <span v-bind="props" class="truncate">
                      {{ getMajors(student).join(', ') }}
                    </span>
                  </template>
                  <div class="pa-2" style="max-width: 360px; white-space: normal;">
                    <div v-for="(m, i) in getMajors(student)" :key="i">{{ m }}</div>
                  </div>
                </v-tooltip>
              </template>
              <span v-else>—</span>
            </div>
          </td>

          <!-- Expand/Collapse -->
          <td class="td-expand">
            <div class="grid-cell ta-right">
              <v-btn
                :id="`expand-${studentKey(student, index)}`"
                :aria-expanded="String(isExpanded(student))"
                :aria-controls="`expand-panel-${studentKey(student, index)}`"
                variant="outlined"
                color="primary"
                size="small"
                class="expand-btn mr-2"
                @click="onToggleExpand(student)"
              >
                <v-icon :icon="isExpanded(student) ? mdiChevronUp : mdiChevronDown" class="mr-1" />
                {{ isExpanded(student) ? 'Hide Courses' : 'View Courses' }}
              </v-btn>

              <v-btn
                color="primary"
                variant="elevated"
                size="small"
                class="text-white mr-2"
                :disabled="!!noteStore.mode"
                @click="openNoteModal(student)"
              >
                + New Note
              </v-btn>
            </div>
          </td>

          <!-- Expansion row -->
          <td
            :id="`expand-panel-${studentKey(student, index)}`"
            class="td-expansion"
          >
            <v-expand-transition>
              <div
                v-if="isExpanded(student)"
                class="grid-cell expansion"
                role="region"
                :aria-label="`Courses for ${getStudentName(student)}`"
              >
                <div class="expansion-content">
                  <!-- per-student spinner inside panel -->
                  <div v-if="isLoading(student)" class="d-flex align-center py-3">
                    <v-progress-circular
                      indeterminate
                      size="16"
                      width="2"
                      class="mr-2"
                    />
                    <span>Loading schedule…</span>
                  </div>

                  <div v-else-if="getAcademicYears(student)" class="border-sm ma-2 pl-4 py-3">
                    <h4 class="mb-2 text-medium-emphasis">Course Schedule</h4>
                    <div
                      v-for="(academicYear, label, yearIndex) in getAcademicYears(student)"
                      :key="label"
                    >
                      <h5 class="sr-only">{{ label }}</h5>
                      <div :class="{'mt-5': yearIndex}" class="align-start d-flex justify-space-between">
                        <div
                          v-for="(enrollments, termId) in academicYear"
                          :key="termId"
                          class="mr-5"
                          :class="{
                            'bg-pale-yellow elevation-1 pb-2 pt-1 px-3': currentEnrollmentTermId === termId.toString(),
                            'pt-1': currentEnrollmentTermId !== termId.toString()
                          }"
                          style="width: 33%"
                        >
                          <TermEnrollmentsTable
                            :enrollments="enrollments"
                            :student-uid="student.uid"
                            :term-id="termId"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-else class="text-medium-emphasis py-2">
                    No enrollment data available.
                  </div>
                </div>
              </div>
            </v-expand-transition>
          </td>
        </tr>
      </tbody>
    </table>
    <EditPeerAdvisingNoteModal
      v-model="isNoteModalOpen"
      :peer-advising-department-id="peerAdvisingDepartmentId"
    />
  </div>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import {mdiChevronDown, mdiChevronUp} from '@mdi/js'
import TermEnrollmentsTable from '@/components/peer/note/TermEnrollmentsTable.vue'
import {getStudentEnrollments} from '@/api/peer-advising-users'
import {useContextStore} from '@/stores/context'
import EditPeerAdvisingNoteModal from '@/components/peer/note/EditPeerAdvisingNoteModal.vue'
import {useNoteStore} from '@/stores/note-edit-session'
import {clearNoteRecipients, getDefaultModel, setNoteRecipient} from '@/stores/note-edit-session/note-edit-session-utils'


type YearTermMap<T = unknown> = Record<string, Record<string, T[]>>

interface Advisor {
  uid: string
  sid: string
  firstName: string
  lastName: string
  email: string
  role: string
  title: string
  program: string
  plan: string
}

interface Student {
  sid: string | number
  uid: string | number
  firstName?: string
  lastName?: string
  name?: string
  email?: string
  majors?: string[]
  advisors?: Advisor[]
  photoUrl?: string
}

const noteStore = useNoteStore()
const isNoteModalOpen = ref(false)

const {students, sidsWithNotes, isFetching, peerAdvisingDepartmentId} = defineProps<{
  students: Student[]
  sidsWithNotes: string[]
  isFetching?: boolean
  peerAdvisingDepartmentId: number | undefined
}>()

const {config} = useContextStore()
const currentEnrollmentTermId = config.currentEnrollmentTermId?.toString?.() ?? ''

// Track expanded rows by uid (fallback to sid)
const expanded = ref<Set<string | number>>(new Set())

// Per-student cache of enrollments (plain nested object: year -> term -> enrollments[])
const academicYearsByStudent = ref(new Map())

// per-student loading state, to show loading status for each students' enrollment data
const loadingByStudent = ref(new Map<string | number, boolean>())

const studentKey = (s: Student, i: number) => s.uid ?? s.sid ?? i
const isExpanded = (s: Student) => expanded.value.has(studentKey(s, 0))
const isLoading = (s: Student) => !!loadingByStudent.value.get(studentKey(s, 0))

// Helpers to update Maps reactively (clone to trigger updates)
function setAcademicYearsFor(key: string | number, data) {
  const m = new Map(academicYearsByStudent.value)
  m.set(key, data)
  academicYearsByStudent.value = m
}
function setLoadingFor(key: string | number, val: boolean) {
  const m = new Map(loadingByStudent.value)
  m.set(key, val)
  loadingByStudent.value = m
}

function openNoteModal(student: Student) {
  noteStore.exitSession()

  const model = getDefaultModel()
  model.subject = '' // Peer advisors don’t provide subject
  model.peerAdvisingDepartmentId = peerAdvisingDepartmentId
  noteStore.setModel(model)
  noteStore.setMode('createPeerAdvisorNote')

  // recipients-based preselect
  clearNoteRecipients()
  if (student?.sid) {
    setNoteRecipient(String(student.sid))
  }

  isNoteModalOpen.value = true
  noteStore.setIsCreateNoteModalOpen(true)
}

const onToggleExpand = (s: Student) => {
  const key = studentKey(s, 0)
  if (expanded.value.has(key)) {
    expanded.value.delete(key)
    return
  }
  expanded.value = new Set()
  expanded.value.add(key)
  // Fetch enrollments once per student
  if (!academicYearsByStudent.value.get(key)) {
    fetchEnrollmentsFor(s)
  }
}

const fetchEnrollmentsFor = (s: Student) => {
  const key = studentKey(s, 0)
  setLoadingFor(key, true)
  getStudentEnrollments(s.sid)
    .then((data) => {
      setAcademicYearsFor(key, normalizeToPlainObject(data))
    })
    .catch(() => {
      setAcademicYearsFor(key, {})
    })
    .then(() => {
      setLoadingFor(key, false)
    })
}

function normalizeToPlainObject<T = unknown>(raw: unknown): YearTermMap<T> {
  if (raw && typeof raw === 'object' && !(raw instanceof Map)) {
    return raw as YearTermMap<T>
  }

  const out: YearTermMap<T> = {}

  // If it's a Map of Maps (year -> term -> enrollments[]), convert to plain objects.
  if (raw instanceof Map) {
    for (const [yearLabel, terms] of raw.entries() as Iterable<[string | number, unknown]>) {
      const yearKey = String(yearLabel)
      out[yearKey] = {}
      if (terms instanceof Map) {
        for (const [termId, enrolls] of terms.entries() as Iterable<[string | number, T[]]>) {
          out[yearKey][String(termId)] = enrolls
        }
      }
    }
  }

  return out
}

const getAcademicYears = (s: Student) => {
  return academicYearsByStudent.value.get(studentKey(s, 0))
}

const getStudentName = (s: Student) =>
  s.name || [s.firstName, s.lastName].filter(Boolean).join(' ') || `SID: ${s.sid}`

const getStudentEmail = (s: Student) => s.email || ''

const getMajors = (s: Student) => Array.isArray(s.majors) ? s.majors : []
</script>

<style scoped>
.bg-alt { background: #fafafa; }
.ta-right { text-align: right; }

/* Ellipsis for long majors line */
.truncate {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-table-wrapper tr {
  display: grid;
  grid-auto-rows: min-content;
    /* Student | UID | Email | Major | Expand Schedule + New Note */
  grid-template-columns: 20% 10% 24% 26% 22%;
  width: 100%;
}

.student-table-wrapper td {
  vertical-align: top;
}

.student-table-wrapper .grid-cell {
  padding: 8px 12px;
}

.td-expansion .grid-cell.expansion {
  grid-area: 2 / 1 / 2 / 6;
  background: #f6fbff;
  border-left: 3px solid #1e88e5;
  margin-top: 8px;
  border-radius: 4px;
}

.td-student   { grid-area: 1 / 1 / 1 / 1; }
.td-sid       { grid-area: 1 / 2 / 1 / 2; }
.td-email     { grid-area: 1 / 3 / 1 / 3; }
.td-major     { grid-area: 1 / 4 / 1 / 4; }
.td-expand    { grid-area: 1 / 5 / 1 / 5; }

.td-expansion { grid-area: 2 / 1 / 2 / 7; }
.td-expansion .grid-cell.expansion {
  grid-area: 2 / 1 / 2 / 7;
}

.student-table-wrapper tr:not(.expanded) td {
  padding-top: 0px;
  padding-bottom: 0px;
}

.expand-btn { font-weight: 500; }

/* Responsive stacking for small screens */
@media (max-width: 959px) {
  .student-table-wrapper {
    overflow: hidden;
    min-width: 300px;
  }
  .student-table-wrapper table, tbody, tr {
    display: block !important;
  }
  .student-table-wrapper td {
    display: block !important;
    max-width: unset !important;
    padding: 2px 8px !important;
    width: 100% !important;
  }
  .student-table-wrapper tr.expanded {
    padding-bottom: 12px !important;
  }
  .td-expand .grid-cell { text-align: left; }
}
</style>
