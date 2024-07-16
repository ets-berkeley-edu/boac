<template>
  <div v-if="key">
    <div v-if="!degreeStore.courses[key].length" class="no-data-text">
      No courses
    </div>
    <div v-if="degreeStore.courses[key].length" :id="`${key}-courses-container`">
      <b-table-simple
        :id="`${key}-courses-table`"
        borderless
        class="mb-1 w-100 table-layout"
        responsive="md"
        small
      >
        <b-thead class="border-bottom">
          <b-tr class="text-no-wrap">
            <b-th v-if="currentUser.canEditDegreeProgress" class="th-course-assignment-menu">
              <span class="sr-only">Options to assign course</span>
            </b-th>
            <b-th class="pl-0 th-name">Course</b-th>
            <b-th class="pl-0 text-right">Units</b-th>
            <b-th class="th-grade">Grade</b-th>
            <b-th v-if="!ignored" class="pl-0">Term</b-th>
            <b-th
              class="pl-0"
              :class="{
                'th-note': hasAnyNotes
              }"
            >
              Note
            </b-th>
            <b-th v-if="currentUser.canEditDegreeProgress"></b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <template v-for="(course, index) in degreeStore.courses[key]" :key="`tr-${index}`">
            <b-tr
              :id="course.manuallyCreatedBy ? `${key}-course-${course.id}-manually-created` : `${key}-course-${course.termId}-${course.sectionId}`"
              class="tr-course"
              :class="{
                'accent-color-blue': course.accentColor === 'Blue',
                'accent-color-green': course.accentColor === 'Green',
                'accent-color-orange': course.accentColor === 'Orange',
                'accent-color-purple': course.accentColor === 'Purple',
                'accent-color-red': course.accentColor === 'Red',
                'border-left border-right border-top': isNoteVisible(course),
                'cursor-grab': canDrag() && !draggingContext.course,
                'mouseover-grabbable': hoverCourseId === course.id && !draggingContext.course,
                'tr-while-dragging': isUserDragging(course.id)
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
              <td v-if="currentUser.canEditDegreeProgress" class="pl-0 td-course-assignment-menu">
                <div v-if="!isUserDragging(course.id)">
                  <CourseAssignmentMenu :after-course-assignment="() => putFocusNextTick(`${key}-header`)" :course="course" />
                </div>
              </td>
              <td class="td-name">
                <div class="align-center d-flex pt-1">
                  <div
                    :class="{
                      'font-weight-500': isEditing(course),
                      'pr-2': course.isCopy
                    }"
                  >
                    {{ course.name }}
                  </div>
                  <div v-if="course.isCopy" class="pr-1">
                    <v-icon :icon="mdiContentCopy" size="sm" />
                  </div>
                </div>
              </td>
              <td class="td-units">
                <v-icon
                  v-if="course.unitRequirements.length"
                  class="fulfillments-icon mr-1 pl-0"
                  :icon="mdiCheckCircleOutline"
                  size="sm"
                  :title="`Counts towards ${oxfordJoin(_map(course.unitRequirements, 'name'))}`"
                />
                <v-icon
                  v-if="unitsWereEdited(course)"
                  :id="course.manuallyCreatedBy ? `${key}-course-${course.id}-manually-created-units-edited` : `${key}-course-${course.termId}-${course.sectionId}-units-edited`"
                  class="changed-units-icon"
                  :icon="mdiInformationOutline"
                  size="sm"
                  :title="`Updated from ${pluralize('unit', course.sis.units)}`"
                />
                <span class="font-size-14">{{ isNil(course.units) ? '&mdash;' : course.units }}</span>
                <span v-if="unitsWereEdited(course)" class="sr-only"> (updated from {{ pluralize('unit', course.sis.units) }})</span>
              </td>
              <td class="td-grade">
                <span class="font-size-14">{{ course.grade || '&mdash;' }}</span>
                <v-icon
                  v-if="isAlertGrade(course.grade)"
                  aria-label="Non-passing grade"
                  :icon="mdiAlertRhombus"
                  class="boac-exclamation ml-1"
                />
              </td>
              <td v-if="!ignored" class="td-term">
                <span class="font-size-14">{{ course.termName }}</span>
              </td>
              <td class="td-note">
                <div v-if="course.note && !isNoteVisible(course) && !degreeStore.isUserDragging(course.id)" class="d-flex justify-content-start">
                  <b-link
                    :id="`course-${course.id}-note`"
                    class="ellipsis-if-overflow"
                    href
                    @click="showNote(course)"
                    v-html="course.note"
                  />
                </div>
                <div v-if="!course.note" :id="`course-${course.id}-note`">&mdash;</div>
              </td>
              <td v-if="currentUser.canEditDegreeProgress" class="td-course-edit-button">
                <div class="d-flex justify-content-end">
                  <div v-if="course.manuallyCreatedBy" class="btn-container">
                    <v-btn
                      v-if="!degreeStore.isUserDragging(course.id)"
                      :id="`delete-${course.id}-btn`"
                      class="pl-0 pr-1 py-0"
                      :disabled="degreeStore.disableButtons"
                      size="small"
                      variant="text"
                      @click="onDelete(course)"
                    >
                      <v-icon :icon="mdiTrashCanOutline" />
                      <span class="sr-only">Delete {{ course.name }}</span>
                    </v-btn>
                  </div>
                  <div class="btn-container">
                    <v-btn
                      v-if="!degreeStore.isUserDragging(course.id)"
                      :id="`edit-${key}-course-${course.id}-btn`"
                      class="font-size-14 pl-0 pr-1 py-0"
                      :disabled="degreeStore.disableButtons"
                      size="small"
                      variant="text"
                      @click="edit(course)"
                    >
                      <v-icon :icon="mdiNoteEditOutline" />
                      <span class="sr-only">Edit {{ course.name }}</span>
                    </v-btn>
                  </div>
                </div>
              </td>
            </b-tr>
            <b-tr v-if="isEditing(course)" :key="`tr-${index}-edit`">
              <b-td colspan="7">
                <EditCourse
                  :after-cancel="afterCancel"
                  :after-save="afterSave"
                  :course="course"
                  :position="0"
                />
              </b-td>
            </b-tr>
            <b-tr
              v-if="isNoteVisible(course)"
              :key="`tr-${index}-note`"
              class="border-bottom border-left border-right"
            >
              <b-td colspan="5" class="px-4">
                <span
                  :id="`${course.id}-note`"
                  aria-live="polite"
                  class="font-size-14"
                  role="alert"
                >
                  <span class="sr-only">Note: </span>
                  {{ course.note }}
                </span>
                <span class="font-size-12 ml-1 text-no-wrap">
                  [<v-btn
                    :id="`course-${course.id}-hide-note-btn`"
                    class="px-0 py-1"
                    size="sm"
                    text="Hide note"
                    variant="text"
                    @click="hideNote(course)"
                  />]
                </span>
              </b-td>
            </b-tr>
          </template>
        </b-tbody>
      </b-table-simple>
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
import {deleteCourse} from '@/stores/degree-edit-session/utils'
import {isAlertGrade} from '@/berkeley'
import {
  mdiAlertRhombus,
  mdiCheckCircleOutline,
  mdiContentCopy,
  mdiInformationOutline, mdiNoteEditOutline,
  mdiTrashCanOutline
} from '@mdi/js'
import {unitsWereEdited} from '@/lib/degree-progress'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {computed, ref} from 'vue'
import {find, get, includes, isNil, remove} from 'lodash'

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

const hasAnyNotes = computed(() => {
  return !!find(degreeStore.courses[key.value], course => course.note)
})

const afterCancel = () => {
  const putFocus = `edit-${key}-course-${courseForEdit.value.id}-btn`
  alertScreenReader('Canceled')
  courseForEdit.value = null
  degreeStore.setDisableButtons(false)
  putFocusNextTick(putFocus)
}

const afterSave = course => {
  courseForEdit.value = null
  alertScreenReader(`Updated ${key} course ${course.name}`)
  degreeStore.setDisableButtons(false)
  putFocusNextTick(`edit-${key}-course-${course.id}-btn`)
}

const edit = course => {
  hideNote(course, false)
  degreeStore.setDisableButtons(true)
  alertScreenReader(`Edit ${key} ${course.name}`)
  courseForEdit.value = course
  putFocusNextTick('name-input')
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
  return deleteCourse(courseForDelete.value.id).then(() => {
    alertScreenReader(`${courseForDelete.value.name} deleted.`)
    isDeleting.value = false
    courseForDelete.value = null
    degreeStore.setDisableButtons(false)
    putFocusNextTick('create-course-button')
  })
}

const hideNote = (course, srAlert=true) => {
  notesVisible.value = remove(notesVisible.value, id => course.id !== id)
  if (srAlert) {
    alertScreenReader('Note hidden')
  }
}

const isEditing = course => {
  return course.sectionId === get(courseForEdit.value, 'sectionId')
}

const isNoteVisible = course => {
  return includes(notesVisible.value, course.id)
}

const onDelete = course => {
  degreeStore.setDisableButtons(true)
  courseForDelete.value = course
  isDeleting.value = true
  alertScreenReader(`Delete ${course.name}`)
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
  alertScreenReader(`Showing note of ${course.name}`)
}
</script>

<style scoped>
table {
  border-collapse: separate;
  border-spacing: 0 0.05em;
}
.btn-container {
  min-width: 20px;
}
.changed-units-icon {
  color: #00c13a;
  margin-right: 0.3em;
}
.ellipsis-if-overflow {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.fulfillments-icon {
  color: #00c13a;
}
.mouseover-grabbable td {
  background-color: #b9dcf0;
}
.mouseover-grabbable td:first-child {
  border-radius: 10px 0 0 10px;
}
.mouseover-grabbable td:last-child {
  border-radius: 0 10px 10px 0;
}
.table-layout {
  table-layout: fixed;
}
.td-course-assignment-menu {
  font-size: 14px;
  padding: 0 0 0 10px;
  vertical-align: middle;
  width: 14px;
}
.td-course-edit-button {
  padding-right: 0;
  vertical-align: middle;
  width: 24px;
}
.td-grade {
  padding: 0 0.5em 0 0.4em;
  vertical-align: middle;
  width: 30px;
}
.td-name {
  font-size: 14px;
  line-height: 95%;
  padding: 0.2em 0 0 0.25em;
  vertical-align: middle;
  width: 72px;
}
.td-note {
  max-width: 100px;
  padding: 0 0.5em 0 0;
  vertical-align: middle;
  width: 1px;
}
.td-term {
  line-height: 90%;
  vertical-align: middle;
  width: 36px;
}
.td-units {
  text-align: right;
  padding: 0 0.5em 0 0;
  vertical-align: middle;
  white-space: nowrap;
  width: 50px;
}
.th-course-assignment-menu {
  padding: 0 0.3em 0 0;
  width: 14px;
}
.th-grade {
  width: 60px;
}
.th-name {
  width: 42px;
}
.th-note {
  width: 100px;
}
.tr-course {
  height: 42px;
}
.tr-while-dragging td {
  background-color: #125074;
  color: white;
}
.tr-while-dragging td:first-child {
  border-radius: 10px 0 0 10px;
}
.tr-while-dragging td:last-child {
  border-radius: 0 10px 10px 0;
}
</style>
