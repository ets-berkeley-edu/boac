<template>
  <div v-if="key">
    <div v-if="!degreeStore.courses[key].length" class="my-2 no-data-text">
      No courses
    </div>
    <div v-if="degreeStore.courses[key].length" :id="`${key}-courses-container`">
      <table
        :id="`${key}-courses-table`"
        class="mb-1 w-100 table-layout"
      >
        <thead class="border-bottom">
          <tr class="text-no-wrap">
            <th v-if="currentUser.canEditDegreeProgress" class="th-assign">
              <span class="sr-only">Options to assign course</span>
            </th>
            <th class="th-course">
              Course
            </th>
            <th class="pr-1 text-right th-units">
              Units
            </th>
            <th class="th-grade">
              Grade
            </th>
            <th v-if="!ignored" class="th-term">
              Term
            </th>
            <th class="pl-0 th-note">
              Note
            </th>
            <th v-if="currentUser.canEditDegreeProgress" class="th-actions" />
          </tr>
        </thead>
        <tbody>
          <template v-for="(course, index) in degreeStore.courses[key]" :key="`tr-${index}`">
            <tr
              :id="course.manuallyCreatedBy ? `${key}-course-${course.id}-manually-created` : `${key}-course-${course.termId}-${course.sectionId}`"
              class="tr-course"
              :class="{
                'accent-color-blue': course.accentColor === 'Blue',
                'accent-color-green': course.accentColor === 'Green',
                'accent-color-orange': course.accentColor === 'Orange',
                'accent-color-purple': course.accentColor === 'Purple',
                'accent-color-red': course.accentColor === 'Red',
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
              <td v-if="currentUser.canEditDegreeProgress" class="td-assign">
                <div v-if="degreeStore.draggingCourseId !== course.id" class="mx-1">
                  <CourseAssignmentMenu :after-course-assignment="() => putFocusNextTick(`${key}-header`)" :course="course" />
                </div>
              </td>
              <td class="overflow-wrap-break-word pt-1 td-name">
                <span :class="{'font-weight-500': isEditing(course), 'mr-2': course.isCopy}">
                  {{ course.name }}
                </span>
                <v-icon
                  v-if="course.isCopy"
                  class="mr-1"
                  :icon="mdiContentCopy"
                  size="sm"
                />
              </td>
              <td class="td-units">
                <v-icon
                  v-if="course.unitRequirements.length"
                  class="fulfillments-icon mr-1 pl-0"
                  :icon="mdiCheckCircleOutline"
                  size="sm"
                  :title="`Counts towards ${oxfordJoin(map(course.unitRequirements, 'name'))}`"
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
              <td v-if="!ignored" class="font-size-14 td-term">
                {{ course.termName }}
              </td>
              <td :class="{'pl-2 td-note truncate-with-ellipsis': course.note, 'pl-3 vertical-top': !course.note}">
                <a
                  v-if="course.note && !isNoteVisible(course)"
                  :id="`course-${course.id}-note`"
                  :class="{'text-decoration-none text-white': degreeStore.draggingCourseId === course.id}"
                  href
                  @click.prevent="showNote(course)"
                  v-html="course.note"
                />
                <div v-if="!course.note" :id="`course-${course.id}-note`">&mdash;</div>
              </td>
              <td
                v-if="currentUser.canEditDegreeProgress"
                class="pr-0 td-action-buttons"
              >
                <div class="d-flex justify-content-end">
                  <div v-if="course.manuallyCreatedBy">
                    <v-btn
                      v-if="degreeStore.draggingCourseId !== course.id"
                      :id="`delete-${course.id}-btn`"
                      :aria-label="`Delete ${course.name}`"
                      class="mr-1 py-0"
                      :class="{'bg-transparent text-primary': !degreeStore.disableButtons}"
                      density="compact"
                      :disabled="degreeStore.disableButtons"
                      flat
                      :icon="mdiTrashCan"
                      size="small"
                      @click="onDelete(course)"
                    />
                  </div>
                  <div>
                    <v-btn
                      v-if="degreeStore.draggingCourseId !== course.id"
                      :id="`edit-${key}-course-${course.id}-btn`"
                      :aria-label="`Edit ${course.name}`"
                      class="mr-1 py-0"
                      :class="{'bg-transparent text-primary': !degreeStore.disableButtons}"
                      density="compact"
                      :disabled="degreeStore.disableButtons"
                      flat
                      :icon="mdiNoteEditOutline"
                      size="small"
                      @click="edit(course)"
                    />
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="isEditing(course)" :key="`tr-${index}-edit`">
              <td class="pb-3 pl-4 pt-1" colspan="7">
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
              <td colspan="5" class="px-4">
                <div
                  :id="`${course.id}-note`"
                  aria-live="polite"
                  class="font-size-14"
                  role="alert"
                >
                  <span class="sr-only">Note: </span>
                  {{ course.note }}
                </div>
                <div class="font-size-12 pb-2 text-no-wrap">
                  [<v-btn
                    :id="`course-${course.id}-hide-note-btn`"
                    class="px-0 py-1 text-primary"
                    size="sm"
                    text="Hide note"
                    variant="text"
                    @click="hideNote(course)"
                  />]
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
import {deleteCourse} from '@/stores/degree-edit-session/utils'
import {isAlertGrade} from '@/berkeley'
import {
  mdiAlertRhombus,
  mdiCheckCircleOutline,
  mdiContentCopy,
  mdiInformationOutline,
  mdiNoteEditOutline,
  mdiTrashCan
} from '@mdi/js'
import {unitsWereEdited} from '@/lib/degree-progress'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {ref} from 'vue'
import {get, includes, isNil, remove} from 'lodash'

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

const isEditing = course => course.id === get(courseForEdit.value, 'id')

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
  border-collapse: collapse;
  border-spacing: 0 0.05em;
  table-layout: fixed;
  width: 100%;
}
.changed-units-icon {
  color: #00c13a;
  margin-right: 0.3em;
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
.td-action-buttons {
  vertical-align: top;
}
.td-assign {
  font-size: 14px;
  vertical-align: top;
  width: 28px !important;
}
.td-grade {
  vertical-align: top;
}
.td-name {
  font-size: 14px;
  vertical-align: top;
}
.td-note {
  max-width: 40px;
  padding-top: 1px;
  vertical-align: top;
}
.td-term {
  padding-top: 2px;
  vertical-align: top;
}
.td-units {
  padding-right: 5px;
  text-align: right;
  vertical-align: top;
  white-space: nowrap;
}
.th-actions {
  max-width: 40px !important;
  width: 40px !important;
}
.th-assign {
  max-width: 28px !important;
  width: 28px !important;
}
.th-course {
  max-width: 100px !important;
  width: 100px !important;
}
.th-grade {
  max-width: 46px !important;
  width: 46px !important;
}
.th-note {
  width: 25% !important;
}
.th-term {
  max-width: 84px !important;
  width: 84px !important;
}
.th-units {
  max-width: 40px !important;
  width: 40px !important;
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
