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
          <th scope="col">UID</th>
          <th scope="col">Email</th>
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
              <span class="font-weight-bold">
                {{ getStudentName(student) }}
              </span>
            </div>
          </td>

          <!-- UID -->
          <td class="td-uid">
            <div class="grid-cell">
              <span class="mono">{{ student.uid ?? '—' }}</span>
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
                class="expand-btn"
                @click="onToggleExpand(student)"
              >
                <v-icon :icon="isExpanded(student) ? mdiChevronUp : mdiChevronDown" class="mr-1" />
                {{ isExpanded(student) ? 'Collapse' : 'View Curriculum' }}
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
                :aria-label="`Curriculum for ${getStudentName(student)}`"
              >
                <div class="expansion-content">
                  <div v-if="isExpanded(student) && getAcademicYears(student)" class="border-sm ma-2 pl-4 py-3">
                    <h4 class="mb-2 text-medium-emphasis">Course Schedule</h4>
                    <div
                      v-for="(academicYear, label, yearIndex) of getAcademicYears(student)"
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
                </div>
              </div>
            </v-expand-transition>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import {mdiChevronDown, mdiChevronUp} from '@mdi/js'
import TermEnrollmentsTable from '@/components/peer/note/TermEnrollmentsTable.vue'
import {getStudentEnrollments} from '@/api/peer-advising-users'
import {useContextStore} from '@/stores/context'

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
  advisors?: Advisor[]
  photoUrl?: string
}

const {students, isFetching} = defineProps<{
  students: Student[]
  isFetching?: boolean
}>()

const {config} = useContextStore()
const currentEnrollmentTermId = config.currentEnrollmentTermId?.toString?.() ?? ''

// Track expanded rows by uid (fallback to sid)
const expanded = ref<Set<string | number>>(new Set())

// Per-student cache of enrollments (plain nested object: year -> term -> enrollments[])
const academicYearsByStudent = ref(new Map())

const studentKey = (s: Student, i: number) => s.uid ?? s.sid ?? i
const isExpanded = (s: Student) => expanded.value.has(studentKey(s, 0))

const onToggleExpand = (s: Student) => {
  const key = studentKey(s, 0)
  if (expanded.value.has(key)) {
    expanded.value.delete(key)
    return
  }
  expanded.value.add(key)
  // Fetch enrollments once per student
  if (!academicYearsByStudent.value.get(key)) {
    fetchEnrollmentsFor(s)
  }
}

const fetchEnrollmentsFor = (s: Student) => {
  const key = studentKey(s, 0)
  getStudentEnrollments(s.sid)
    .then((data) => {
      academicYearsByStudent.value.set(key, normalizeToPlainObject(data))
    })
    .catch(() => {
      academicYearsByStudent.value.set(key, {}) // cache empty to avoid re-fetch loop
    })
}

// Keep your template’s object-style v-for by normalizing to plain objects.
function normalizeToPlainObject(raw) {
  // If already a plain object in desired shape, return as-is
  if (raw && typeof raw === 'object' && !(raw instanceof Map)) {
    return raw
  }
  // If nested Maps, convert to plain objects
  const out = {}
  if (raw instanceof Map) {
    for (const [yearLabel, terms] of raw.entries()) {
      out[yearLabel] = {}
      if (terms instanceof Map) {
        for (const [termId, enrolls] of terms.entries()) {
          (out[yearLabel])[String(termId)] = enrolls
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
</script>

<style scoped>
.bg-alt { background: #fafafa; }
.ta-right { text-align: right; }

.student-table-wrapper tr {
  display: grid;
  grid-auto-rows: min-content;
  grid-template-columns: 32% 18% 35% 15%;
  width: 100%;
}

.student-table-wrapper td {
  vertical-align: top;
}

.student-table-wrapper .grid-cell {
  padding: 8px 12px;
}

.td-expansion .grid-cell.expansion {
  grid-area: 2 / 1 / 2 / 5;
  background: #f6fbff;
  border-left: 3px solid #1e88e5;
  margin-top: 8px;
  border-radius: 4px;
}

.td-student  { grid-area: 1 / 1 / 1 / 1; }
.td-uid      { grid-area: 1 / 2 / 1 / 2; }
.td-email    { grid-area: 1 / 3 / 1 / 3; }
.td-expand   { grid-area: 1 / 4 / 1 / 4; }
.td-expansion{ grid-area: 2 / 1 / 2 / 5; }

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
