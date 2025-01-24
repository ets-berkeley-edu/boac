<template>
  <div v-if="key">
    <div v-if="!degreeStore.courses[key].length" class="no-data-text py-1">
      No courses
    </div>
    <div v-if="degreeStore.courses[key].length" :id="`${key}-courses-container`">
      <table
        :id="`${key}-courses-table`"
        class="mb-1 w-100 table-layout"
      >
        <caption class="sr-only">{{ capitalize(key) }} Courses</caption>
        <thead class="border-b-sm">
          <tr class="text-no-wrap">
            <th v-if="currentUser.canEditDegreeProgress" class="force-width-18"><span class="sr-only">Options to assign course</span></th>
            <th class="font-size-11 force-width-80 pr-1">Course</th>
            <th class="font-size-11 force-width-24 truncate-with-ellipsis" title="Grade">Grade</th>
            <th class="font-size-11 force-width-24 text-right truncate-with-ellipsis pr-2" title="Units">Units</th>
            <th v-if="!ignored" class="font-size-11 force-width-42">Term</th>
            <th class="font-size-11 force-width-50">Note</th>
            <th v-if="currentUser.canEditDegreeProgress" class="force-width-20" />
          </tr>
        </thead>
        <tbody>
          <template v-for="(course, index) in degreeStore.courses[key]" :key="`tr-${index}`">
            <tr
              :id="course.manuallyCreatedBy ? `${key}-course-${course.id}-manually-created` : `${key}-course-${course.termId}-${course.sectionId}`"
              class="tr-course"
              :class="{
                'accent-blue': course.accentColor === 'Blue',
                'accent-green': course.accentColor === 'Green',
                'accent-orange': course.accentColor === 'Orange',
                'accent-purple': course.accentColor === 'Purple',
                'accent-red': course.accentColor === 'Red',
                'border-e-md border-s-md border-t-md': isNoteVisible(course),
                'cursor-grab': canDrag() && !degreeStore.draggingContext.course,
                'mouseover-grabbable': hoverCourseId === course.id && !degreeStore.draggingContext.course,
                'tr-while-dragging': degreeStore.draggingCourseId === course.id
              }"
              :draggable="canDrag()"
              @dragend="onDrag($event, 'end', course)"
              @dragenter="onDrag($event, 'enter', course)"
              @dragleave="onDrag($event, 'leave', course)"
              @dragover="onDrag($event, 'over', course)"
              @dragstart="onDrag($event, 'start', course)"
              @mouseenter="onMouse('enter', course)"
              @mouseleave="onMouse('leave', course)"
            >
              <td
                v-if="currentUser.canEditDegreeProgress"
                class="force-width-18 td-assign"
              >
                <div v-if="degreeStore.draggingCourseId !== course.id">
                  <CourseAssignmentMenu :after-course-assignment="() => afterCourseAssignment(index, key)" :course="course" />
                </div>
              </td>
              <td class="overflow-wrap-break-word td-name">
                <span
                  :class="{
                    'font-weight-500': isEditing(course),
                    'mr-1': course.isCopy,
                    'demo-mode-blur': currentUser.inDemoMode
                  }"
                >
                  {{ course.name }}
                </span>
                <v-icon
                  v-if="course.isCopy"
                  class="mb-1 mr-1"
                  color="info"
                  :icon="mdiContentCopy"
                  size="16"
                  title="Duplicated"
                />
              </td>
              <td
                class="td-grade text-no-wrap"
                :class="{
                  'force-width-24': isAlertGrade(course.grade),
                  'force-width-50': isAlertGrade(course.grade)
                }"
              >
                <span class="font-size-14">{{ course.grade || '&mdash;' }}</span>
                <v-icon
                  v-if="isAlertGrade(course.grade)"
                  class="mb-1"
                  color="warning"
                  :icon="mdiAlert"
                  size="20"
                  title="Non-passing grade"
                />
              </td>
              <td class="td-units text-right">
                <span class="font-size-14">{{ isNil(course.units) ? '&mdash;' : course.units }}</span>
                <span v-if="unitsWereEdited(course)" class="sr-only"> (updated from {{ pluralize('unit', course.sis.units) }})</span>
                <v-icon
                  v-if="course.unitRequirements.length"
                  class="pl-0"
                  color="accent-green"
                  :icon="mdiCheckCircleOutline"
                  size="18"
                  :title="`Counts towards ${oxfordJoin(map(course.unitRequirements, 'name'))}`"
                />
                <v-icon
                  v-if="unitsWereEdited(course)"
                  :id="course.manuallyCreatedBy ? `${key}-course-${course.id}-manually-created-units-edited` : `${key}-course-${course.termId}-${course.sectionId}-units-edited`"
                  class="changed-units-icon"
                  color="accent-green"
                  :icon="mdiInformation"
                  size="18"
                  :title="`Updated from ${pluralize('unit', course.sis.units)}`"
                />
              </td>
              <td v-if="!ignored" class="font-size-14 force-width-42 td-term">
                {{ abbreviateTerm(course.termName) }}
              </td>
              <td
                class="font-size-14 td-note pr-1"
                :class="{
                  'force-width-50': course.note && !isNoteVisible(course),
                  'truncate-with-ellipsis': course.note
                }"
              >
                <a
                  v-if="course.note && !isNoteVisible(course)"
                  :id="`course-${course.id}-note`"
                  :aria-description="`Show note for ${course.name}`"
                  :aria-expanded="false"
                  :class="{'text-decoration-none text-white': degreeStore.draggingCourseId === course.id}"
                  href
                  role="button"
                  @click.prevent="showNote(course)"
                  v-html="course.note"
                />
                <div v-if="!course.note" :id="`course-${course.id}-note`">&mdash;</div>
              </td>
              <td
                v-if="currentUser.canEditDegreeProgress"
              >
                <div class="d-flex h-100 justify-end">
                  <div class="degree-check-action-buttons d-flex pt-1 text-no-wrap">
                    <v-btn
                      v-if="degreeStore.draggingCourseId !== course.id"
                      :id="`edit-${key}-course-${course.id}-btn`"
                      :aria-label="`Edit ${course.name}`"
                      :color="degreeStore.disableButtons ? 'grey' : 'primary'"
                      density="compact"
                      flat
                      :icon="mdiNoteEditOutline"
                      size="small"
                      variant="text"
                      @click="degreeStore.disableButtons ? noop : edit(course)"
                    />
                    <v-btn
                      v-if="course.manuallyCreatedBy && degreeStore.draggingCourseId !== course.id"
                      :id="`delete-${course.id}-btn`"
                      :aria-label="`Delete ${course.name}`"
                      :class="{'bg-transparent text-primary': !degreeStore.disableButtons}"
                      density="compact"
                      :disabled="degreeStore.disableButtons"
                      flat
                      :icon="mdiTrashCan"
                      size="small"
                      @click="onDelete(course)"
                    />
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="isEditing(course)" :key="`tr-${index}-edit`">
              <td class="pb-3" :colspan="currentUser.canEditDegreeProgress ? (ignored ? 6 : 7) : (ignored ? 4 : 5)">
                <EditCourse
                  :after-cancel="afterCancel"
                  :after-save="afterSave"
                  :course="course"
                  :position="0"
                />
              </td>
            </tr>
            <tr
              v-if="isNoteVisible(course)"
              :key="`tr-${index}-note`"
              class="border-b-md border-e-md border-s-md"
            >
              <td class="px-4" :colspan="currentUser.canEditDegreeProgress ? (ignored ? 6 : 7) : (ignored ? 4 : 5)">
                <div class="d-flex flex-column-reverse">
                  <div class="font-size-12 py-2 text-no-wrap">
                    [<v-btn
                      :id="`course-${course.id}-hide-note-btn`"
                      :aria-expanded="true"
                      class="pa-1 text-primary"
                      size="sm"
                      text="Hide note"
                      variant="text"
                      @click="hideNote(course)"
                    />]
                  </div>
                  <div
                    :id="`${course.id}-note`"
                    aria-live="polite"
                    class="font-size-14"
                  >
                    <span class="sr-only">Note: </span>
                    {{ course.note }}
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
    <AreYouSureModal
      v-model="isDeleting"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      button-label-confirm="Delete"
      modal-header="Delete Course"
    >
      Are you sure you want to delete <strong>&quot;{{ courseForDelete.name }}&quot;</strong>?
    </AreYouSureModal>
  </div>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import CourseAssignmentMenu from '@/components/degree/student/CourseAssignmentMenu'
import EditCourse from '@/components/degree/student/EditCourse'
import {alertScreenReader, oxfordJoin, pluralize, putFocusNextTick} from '@/lib/utils'
import {capitalize, get, includes, isNil, map, noop, remove, size} from 'lodash'
import {deleteCourse} from '@/stores/degree-edit-session/utils'
import {isAlertGrade} from '@/berkeley'
import {
  mdiAlert,
  mdiCheckCircleOutline,
  mdiContentCopy,
  mdiInformation,
  mdiNoteEditOutline,
  mdiTrashCan
} from '@mdi/js'
import {unitsWereEdited} from '@/lib/degree-progress'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {ref} from 'vue'

const contextStore = useContextStore()
const degreeStore = useDegreeStore()

const currentUser = contextStore.currentUser

const props = defineProps({
  ignored: {
    required: false,
    type: Boolean
  }
})

const courseForDelete = ref(undefined)
const courseForEdit = ref(undefined)
const hoverCourseId = ref(undefined)
const isDeleting = ref(false)
const key = props.ignored ? 'ignored' : 'unassigned'
const notesVisible = ref([])

const abbreviateTerm = (termName) => {
  if (termName) {
    return termName.replace('Spring', 'Spr').replace('Summer', 'Sum')
  }
}

const afterCancel = () => {
  const putFocus = `edit-${key}-course-${courseForEdit.value.id}-btn`
  alertScreenReader('Canceled')
  courseForEdit.value = null
  degreeStore.setDisableButtons(false)
  putFocusNextTick(putFocus)
}

const afterCourseAssignment = (index, key) => {
  const lastItemIndex = size(degreeStore.courses[key]) - 1
  if (lastItemIndex >= 0) {
    const nextFocusIndex = index > lastItemIndex ? index - 1 : index
    const nextFocusCourse = get(degreeStore.courses[key], nextFocusIndex)
    if (nextFocusCourse) {
      putFocusNextTick(`assign-course-${nextFocusCourse.id}-btn`)
    }
  } else {
    putFocusNextTick(`${key}-header`)
  }
}

const afterSave = course => {
  courseForEdit.value = null
  alertScreenReader(`${key} course ${course.name} saved.`)
  degreeStore.setDisableButtons(false)
  putFocusNextTick(`edit-${key}-course-${course.id}-btn`)
}

const canDrag = () => {
  return !degreeStore.disableButtons && currentUser.canEditDegreeProgress
}

const deleteCanceled = () => {
  putFocusNextTick(`delete-${courseForDelete.value.id}-btn`)
  isDeleting.value = false
  courseForDelete.value = null
  alertScreenReader('Canceled. Nothing deleted.')
  degreeStore.setDisableButtons(false)
}

const deleteConfirmed = () => {
  alertScreenReader(`Deleting ${courseForDelete.value.name}`)
  deleteCourse(courseForDelete.value.id).then(() => {
    alertScreenReader(`Deleted ${courseForDelete.value.name}.`)
    isDeleting.value = false
    courseForDelete.value = null
    degreeStore.setDisableButtons(false)
    putFocusNextTick('create-course-button')
  })
}

const edit = course => {
  hideNote(course, false)
  degreeStore.setDisableButtons(true)
  courseForEdit.value = course
  putFocusNextTick(course.manuallyCreatedBy ? 'course-name-input' : 'course-units-input')
}

const hideNote = (course, srAlert=true) => {
  notesVisible.value = remove(notesVisible.value, id => course.id !== id)
  if (srAlert) {
    alertScreenReader('Collapsed')
    putFocusNextTick(`course-${course.id}-note`)
  }
}

const isEditing = course => course.id === get(courseForEdit.value, 'id')

const isNoteVisible = course => {
  return includes(notesVisible.value, course.id)
}

const onDelete = course => {
  degreeStore.setDisableButtons(true)
  courseForDelete.value = course
  isDeleting.value = true
}

const onDrag = (event, stage, course) => {
  switch (stage) {
  case 'end':
    if (event.target) {
      event.target.style.opacity = 1
    }
    degreeStore.draggingContextReset()
    break
  case 'start':
    if (event.target) {
      // Required for Safari
      event.target.style.opacity = 0.9
    }
    degreeStore.dragStart(course, key)
    break
  case 'enter':
  case 'exit':
  case 'leave':
  case 'over':
  default:
    break
  }
}

const onMouse = (stage, course) => {
  switch(stage) {
  case 'enter':
    if (canDrag() && !degreeStore.draggingContext.course) {
      hoverCourseId.value = course.id
    }
    break
  case 'leave':
    hoverCourseId.value = null
    break
  default:
    break
  }
}

const showNote = course => {
  notesVisible.value.push(course.id)
  alertScreenReader('Expanded')
  putFocusNextTick(`course-${course.id}-hide-note-btn`)
}
</script>

<style scoped>
table {
  border-collapse: collapse;
  border-spacing: 0 0.05em;
  table-layout: fixed;
  width: 100%;
}
tbody:before {
  content: '';
  display: block;
  height: 10px;
}
th {
  height: 20px;
  padding-bottom: 5px;
}
.changed-units-icon {
  margin-left: 0.1em;
}
.table-layout {
  table-layout: fixed;
}
.td-assign {
  font-size: 14px;
  vertical-align: top;
}
.td-grade {
  padding-top: 1px;
  vertical-align: top;
}
.td-name {
  font-size: 14px;
  padding-top: 3px;
  vertical-align: top;
}
.td-note {
  padding-top: 3px;
  vertical-align: top;
}
.td-term {
  padding-top: 3px;
  vertical-align: top;
}
.td-units {
  padding: 1px 8px 0 0;
  vertical-align: top;
  white-space: nowrap;
}
.tr-course td {
  height: 40px !important;
}
.tr-while-dragging td {
  background-color: rgb(var(--v-theme-tertiary));
  color: rgb(var(--v-theme-on-tertiary));
}
.tr-while-dragging td:first-child {
  border-radius: 10px 0 0 10px;
}
.tr-while-dragging td:last-child {
  border-radius: 0 10px 10px 0;
}
</style>
