<template>
  <div>
    <div>
      <table
        :id="`column-${position}-courses-of-category-${parentCategory.id}`"
        class="mb-0 w-100"
      >
        <thead class="border-b-md">
          <tr class="sortable-table-header text-no-wrap">
            <th v-if="hasAssignedCourses && canEdit" class="px-0 th-course-assignment-menu">
              <span v-if="hasAssignedCourses" class="sr-only">Options to re-assign course</span>
              <span v-if="!hasAssignedCourses" class="sr-only">Recommended?</span>
            </th>
            <th v-if="!isCampusRequirements" :class="{'font-size-12': printable}">Course</th>
            <th v-if="isCampusRequirements" :class="{'font-size-12': printable}">Requirement</th>
            <th v-if="!isCampusRequirements && items.length" class="pr-2 text-right" :class="{'font-size-12': printable}">Units</th>
            <th v-if="degreeStore.sid && !isCampusRequirements" :class="{'font-size-12': printable}">Grade</th>
            <th v-if="degreeStore.sid && isCampusRequirements" class="pl-0 pr-2 text-center" :class="{'font-size-12': printable}">Satisfied</th>
            <th
              v-if="degreeStore.sid"
              class="pl-0"
              :class="{
                'font-size-12': printable,
                'th-note': hasAnyNotes
              }"
            >
              Note
            </th>
            <th v-if="!degreeStore.sid && !isCampusRequirements && items.length" class="px-0" :class="{'font-size-12': printable}">Fulfillment</th>
            <th v-if="canEdit && (degreeStore.sid || !isCampusRequirements)" class="px-0 sr-only">Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(bundle, index) in categoryCourseBundles" :key="`tr-${index}`">
            <tr
              :id="`course-${bundle.category.id}-table-row-${index}`"
              :class="{
                'accent-color-blue': getAccentColor(bundle) === 'Blue',
                'accent-color-green': getAccentColor(bundle) === 'Green',
                'accent-color-orange': getAccentColor(bundle) === 'Orange',
                'accent-color-purple': getAccentColor(bundle) === 'Purple',
                'accent-color-red': getAccentColor(bundle) === 'Red',
                'border-left border-right border-top': isNoteVisible(bundle),
                'cursor-grab': isDraggable(bundle),
                'drop-zone-on': isDroppable(bundle.category),
                'mouseover-grabbable': bundle.course && hoverCourseId === bundle.course.id && !degreeStore.draggingContext.course,
                'tr-while-dragging': bundle.course && degreeStore.isUserDragging(bundle.course.id)
              }"
              :draggable="isDraggable(bundle)"
              @dragend="onDrag($event, 'end', bundle)"
              @dragenter="onDrag($event, 'enter', bundle)"
              @dragleave="onDrag($event, 'leave', bundle)"
              @dragover="onDrag($event, 'over', bundle)"
              @dragstart="onDrag($event, 'start', bundle)"
              @drop="onDropCourse($event, bundle.category, 'requirement')"
              @mouseenter="onMouse('enter', bundle)"
              @mouseleave="onMouse('leave', bundle)"
            >
              <td
                v-if="hasAssignedCourses && canEdit && !isCampusRequirements"
                class="pt-1 pl-0 td-course-assignment-menu"
              >
                <div
                  v-if="bundle.course && canEdit && !degreeStore.isUserDragging(bundle.course.id)"
                  :id="`assign-course-${bundle.course.id}-menu-container`"
                >
                  <CourseAssignmentMenu
                    v-if="bundle.course.categoryId"
                    :after-course-assignment="course => putFocusNextTick(`assign-course-${course.id}-dropdown`, 'button')"
                    :course="bundle.course"
                  />
                </div>
              </td>
              <td
                class="font-size-14 pl-0"
                :class="{
                  'text-grey font-italic': !isSatisfied(bundle) && !getAccentColor(bundle),
                  'font-size-12 td-name-printable': printable,
                  'font-size-14 td-name': !printable
                }"
              >
                <div class="align-center d-flex pt-1">
                  <div v-if="!bundle.course && bundle.category.isRecommended" class="pr-1">
                    <v-icon
                      :id="`category-${bundle.category.id}-is-recommended`"
                      class="accent-color-orange"
                      :icon="mdiCircleOutline"
                      title="Recommended"
                    />
                    <span class="sr-only">This is a recommended course requirement</span>
                  </div>
                  <div
                    :class="{
                      'accent-color-purple': get(bundle.category, 'isSatisfiedByTransferCourse'),
                      'font-weight-500': isEditing(bundle),
                      'pr-2': get(bundle.course, 'isCopy')
                    }"
                  >
                    <span
                      class="pl-1"
                      :class="{'text-strikethrough': get(bundle.category, 'isIgnored')}"
                    >
                      <!-- Spaces surrounding 'name' make life easier for QA. Do not trim. -->
                      {{ bundle.name }}
                    </span>
                  </div>
                  <div v-if="get(bundle.course, 'isCopy')" class="pr-1">
                    <v-icon
                      :icon="mdiContentCopy"
                      size="sm"
                      title="Course satisfies multiple requirements."
                    />
                  </div>
                </div>
              </td>
              <td
                v-if="!isCampusRequirements"
                class="td-units"
                :class="{
                  'text-grey font-italic': !bundle.course && !getAccentColor(bundle)
                }"
              >
                <v-icon
                  v-if="isCourseFulfillmentsEdited(bundle)"
                  class="fulfillments-icon mr-1"
                  :icon="mdiCheckCircleOutline"
                  size="sm"
                  :title="bundle.course.unitRequirements.length ? `Counts towards ${oxfordJoin(getCourseFulfillments(bundle))}.` : 'Fulfills no unit requirements'"
                />
                <v-icon
                  v-if="unitsWereEdited(bundle.course)"
                  :id="`units-were-edited-${bundle.course.id}`"
                  class="changed-units-icon"
                  :icon="mdiInformationOutline"
                  size="sm"
                  :title="`Updated from ${pluralize('unit', bundle.course.sis.units)}`"
                />
                <div :class="{'font-size-12': printable, 'font-size-14': !printable}">{{ isNil(bundle.units) ? '&mdash;' : bundle.units }}</div>
                <span v-if="unitsWereEdited(bundle.course)" class="sr-only"> (updated from {{ pluralize('unit', bundle.course.sis.units) }})</span>
              </td>
              <td v-if="degreeStore.sid && !isCampusRequirements" class="td-grade">
                <span
                  :class="{
                    'text-grey font-italic': !bundle.course && !getAccentColor(bundle),
                    'font-size-12': printable,
                    'font-size-14 text-no-wrap': !printable
                  }"
                >
                  {{ getGrade(bundle) }}
                </span>
                <v-icon
                  v-if="isAlertGrade(getGrade(bundle))"
                  aria-label="Non-passing grade"
                  :icon="mdiAlertRhombus"
                  class="boac-exclamation ml-1"
                />
              </td>
              <td v-if="degreeStore.sid && isCampusRequirements" class="td-satisfied">
                <CampusRequirementCheckbox
                  :campus-requirement="bundle"
                  :position="position"
                  :printable="printable"
                />
              </td>
              <td
                v-if="degreeStore.sid"
                :class="{
                  'text-grey font-italic': !isSatisfied(bundle) && !getAccentColor(bundle),
                  'font-size-12 td-note-printable': printable,
                  'truncate-with-ellipsis font-size-14 td-note': !printable
                }"
              >
                <div
                  v-if="printable"
                  :id="`${bundle.course ? 'course' : 'category'}-${bundle.id}-note`"
                  class="font-size-12"
                  v-html="getNote(bundle)"
                />
                <div
                  v-if="!printable && getNote(bundle) && !isNoteVisible(bundle)"
                  class="d-flex font-size-14 justify-content-start"
                >
                  <a
                    :id="`${bundle.course ? 'course' : 'category'}-${bundle.id}-note`"
                    class="truncate-with-ellipsis"
                    href="#"
                    @click="showNote(bundle)"
                    v-html="getNote(bundle)"
                  />
                </div>
                <div
                  v-if="!getNote(bundle)"
                  :id="`${bundle.course ? 'course' : 'category'}-${bundle.id}-note`"
                >
                  &mdash;
                </div>
              </td>
              <td
                v-if="!degreeStore.sid && !isCampusRequirements"
                class="align-middle td-max-width-0"
                :class="{
                  'text-grey font-italic': !bundle.course && !getAccentColor(bundle),
                  'font-size-12': printable,
                  'font-size-14': !printable
                }"
                :title="oxfordJoin(map(bundle.unitRequirements, 'name'), 'None')"
              >
                <div class="align-items-start d-flex justify-space-between">
                  <div class="truncate-with-ellipsis">
                    <span>
                      {{ oxfordJoin(map(bundle.unitRequirements, 'name'), '&mdash;') }}
                    </span>
                  </div>
                  <div v-if="size(bundle.unitRequirements) > 1" class="unit-requirement-count">
                    <span class="sr-only">(Has </span>{{ bundle.unitRequirements.length }}<span class="sr-only"> requirements.)</span>
                  </div>
                </div>
              </td>
              <td v-if="canEdit && (degreeStore.sid || !isCampusRequirements)" class="td-actions">
                <div class="d-flex justify-content-end text-no-wrap">
                  <div class="btn-container">
                    <v-btn
                      v-if="!degreeStore.isUserDragging(get(bundle.course, 'id'))"
                      :id="`column-${position}-edit-${bundle.key}-btn`"
                      class="pl-0 pr-1 py-0"
                      :disabled="degreeStore.disableButtons"
                      size="small"
                      variant="text"
                      @click="edit(bundle)"
                    >
                      <v-icon :icon="mdiNoteEditOutline" />
                      <span class="sr-only">Edit {{ bundle.name }}</span>
                    </v-btn>
                  </div>
                  <div class="btn-container">
                    <v-btn
                      v-if="!degreeStore.sid || (bundle.course && (bundle.course.isCopy || bundle.course.manuallyCreatedBy)) && !degreeStore.isUserDragging(get(bundle.course, 'id'))"
                      :id="`column-${position}-delete-${bundle.key}-btn`"
                      class="pl-0 pr-1 py-0"
                      :disabled="degreeStore.disableButtons"
                      size="small"
                      variant="text"
                      @click="onDelete(bundle)"
                    >
                      <v-icon :icon="mdiTrashCanOutline" />
                      <span class="sr-only">Delete {{ bundle.name }}</span>
                    </v-btn>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="isEditing(bundle)" :key="`tr-${index}-edit`">
              <td class="pa-0" colspan="6">
                <EditCourse
                  v-if="bundle.course"
                  :after-cancel="afterCancel"
                  :after-save="afterSave"
                  :course="bundle.course"
                  :position="position"
                />
                <EditCategory
                  v-if="!bundle.course && !degreeStore.sid"
                  :after-cancel="afterCancel"
                  :after-save="afterSave"
                  :existing-category="bundle.category"
                  :position="position"
                />
                <EditCourseRequirement
                  v-if="!bundle.course && degreeStore.sid"
                  :after-cancel="afterCancel"
                  :after-save="afterSave"
                  :category="bundle.category"
                  :position="position"
                />
              </td>
            </tr>
            <tr
              v-if="isNoteVisible(bundle)"
              :key="`tr-${index}-note`"
              class="border-bottom border-left border-right"
            >
              <td colspan="5" class="px-2">
                <span
                  :id="bundle.course ? `course-${bundle.course.id}-note` : `category-${bundle.category.id}-note`"
                  aria-live="polite"
                  class="font-size-14"
                  role="alert"
                >
                  <span class="sr-only">Note: </span>
                  {{ getNote(bundle) }}
                </span>
                <span class="font-size-12 ml-1 text-no-wrap">
                  [<v-btn
                    :id="`column-${position}-${bundle.key}-hide-note-btn`"
                    class="px-0 py-1"
                    size="small"
                    text="Hide note"
                    variant="text"
                    @click="hideNote(bundle)"
                  />]
                </span>
              </td>
            </tr>
          </template>
          <tr v-if="!items.length">
            <td class="pa-2" :class="{'pb-3': !degreeStore.sid}" colspan="5">
              <span
                :id="emptyCategoryId"
                class="text-grey font-italic"
                :class="{
                  'font-size-14': printable,
                  'font-size-16': !printable
                }"
              >
                No completed requirements
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="degreeStore.sid && canEdit && !isCampusRequirements" class="mb-3" :class="{'mt-1': !items.length}">
      <CreateCourseModal :parent-category="parentCategory" />
    </div>
    <AreYouSureModal
      v-model="isDeleting"
      button-label-confirm="Delete"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      modal-header="Delete Course"
    >
      Are you sure you want to delete <strong>&quot;{{ bundleForDelete.name }}&quot;</strong>
    </AreYouSureModal>
  </div>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import CampusRequirementCheckbox from '@/components/degree/student/CampusRequirementCheckbox'
import CourseAssignmentMenu from '@/components/degree/student/CourseAssignmentMenu'
import CreateCourseModal from '@/components/degree/student/CreateCourseModal'
import EditCategory from '@/components/degree/EditCategory'
import EditCourse from '@/components/degree/student/EditCourse'
import EditCourseRequirement from '@/components/degree/student/EditCourseRequirement'
import {alertScreenReader, oxfordJoin, pluralize, putFocusNextTick} from '@/lib/utils'
import {computed, ref} from 'vue'
import {deleteCategory, deleteCourse, onDrop} from '@/stores/degree-edit-session/utils'
import {each, every, find, get, includes, isEmpty, isNil, map, remove, size, xorBy} from 'lodash'
import {
  findCategoryById,
  getAssignedCourses,
  getCourseKey,
  isCampusRequirement,
  unitsWereEdited
} from '@/lib/degree-progress'
import {isAlertGrade} from '@/berkeley'
import {
  mdiAlertRhombus,
  mdiCheckCircleOutline,
  mdiCircleOutline,
  mdiContentCopy,
  mdiInformationOutline,
  mdiNoteEditOutline, mdiTrashCanOutline
} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'

const props = defineProps({
  items: {
    required: true,
    type: Array
  },
  parentCategory: {
    required: true,
    type: Object
  },
  position: {
    required: true,
    type: Number
  },
  printable: {
    required: false,
    type: Boolean
  }
})

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const degreeStore = useDegreeStore()
const bundleForDelete = ref(undefined)
const bundleForEdit = ref(undefined)
const canEdit = currentUser.canEditDegreeProgress && !props.printable
const emptyCategoryId = `empty-category-${props.parentCategory.id}`
const hoverCourseId = ref(undefined)
const isDeleting = ref(false)
const notesVisible = ref([])

const categoryCourseBundles = computed(() => {
  const transformed = []
  each(props.items, item => {
    let category
    let course
    if (item.categoryType) {
      category = item
      course = category.courses.length ? getCourse(category.courses[0].id) : null
    } else {
      course = item
      category = findCategoryById(course.categoryId)
    }
    transformed.push({
      category,
      course,
      key: course ? `course-${course.id}` : `category-${category.id}`,
      name: getBundleName(course, category),
      type: course ? 'course' : 'category',
      units: course ? course.units : describeCategoryUnits(category),
      unitRequirements: (course || category).unitRequirements
    })
  })
  return transformed
})

const hasAnyNotes = computed(() => {
  return !!find(categoryCourseBundles.value, bundle => getNote(bundle))
})

const hasAssignedCourses = computed(() => {
  return !!find(categoryCourseBundles.value, bundle => bundle.course)
})

const isCampusRequirements = computed(() => {
  return !isEmpty(props.items) && every(props.items, isCampusRequirement)
})

const afterCancel = () => {
  alertScreenReader('Canceled')
  putFocusNextTick(`column-${props.position}-edit-${bundleForEdit.value.key}-btn`)
  bundleForEdit.value = null
  degreeStore.setDisableButtons(false)
}

const afterSave = () => {
  alertScreenReader(`Updated ${bundleForEdit.value.type} ${bundleForEdit.value.name}`)
  putFocusNextTick(`column-${props.position}-edit-${bundleForEdit.value.key}-btn`)
  bundleForEdit.value = null
  degreeStore.setDisableButtons(false)
}

const getCourse = courseId => {
  return find(degreeStore.courses.assigned.concat(degreeStore.courses.unassigned), ['id', courseId])
}

const deleteCanceled = () => {
  putFocusNextTick(`column-${props.position}-delete-${bundleForDelete.value.key}-btn`)
  isDeleting.value = false
  bundleForDelete.value = null
  alertScreenReader('Canceled. Nothing deleted.')
  degreeStore.setDisableButtons(false)
}

const deleteConfirmed = () => {
  const name = bundleForDelete.value.name
  const done = () => {
    alertScreenReader(`${name} deleted.`)
    const putFocus = degreeStore.sid ? `column-${props.position}-add-course-to-category-${props.parentCategory.id}` : 'page-header'
    isDeleting.value = false
    bundleForDelete.value = null
    degreeStore.setDisableButtons(false)
    putFocusNextTick(putFocus)
  }
  let promise = undefined
  if (degreeStore.sid) {
    promise = deleteCourse(bundleForDelete.value.course.id).then(done)
  } else {
    promise = deleteCategory(bundleForDelete.value.category.id).then(done)
  }
  return promise
}

const describeCategoryUnits = category => {
  if (category) {
    const showRange = category.unitsUpper && category.unitsLower !== category.unitsUpper
    return showRange ? `${category.unitsLower}-${category.unitsUpper}` : category.unitsLower
  } else {
    return null
  }
}

const edit = bundle => {
  hideNote(bundle, false)
  hoverCourseId.value = null
  degreeStore.setDisableButtons(true)
  alertScreenReader(`Edit ${bundle.name}`)
  bundleForEdit.value = bundle
}

const getAccentColor = bundle => bundle.course ? bundle.course.accentColor : bundle.category.accentColor

const getBundleName = (course, category) => {
  let name = (course || category).name
  if (course && props.printable) {
    each(['COL', 'DIS', 'FLD', 'GRP', 'IND', 'LAB', 'LEC', 'SEM'], format => {
      const trimmed = name.replace(new RegExp(` ${format} [0-9]+$`), '')
      if (trimmed !== name) {
        name = trimmed
        return false
      }
    })
  }
  return name
}

const getCourseFulfillments = bundle => {
  return bundle.course ? map(bundle.course.unitRequirements, 'name') : []
}

const getGrade = bundle => {
  return get(bundle.course || bundle.category, 'grade')
}
const getNote = bundle => bundle.course ? bundle.course.note : bundle.category.note

const hideNote = (bundle, srAlert=true) => {
  notesVisible.value = remove(notesVisible.value, key => bundle.key !== key)
  if (srAlert) {
    alertScreenReader('Note hidden')
  }
}

const isCourseFulfillmentsEdited = bundle => {
  if (bundle.category && bundle.course) {
    const edited = xorBy(bundle.category.unitRequirements, bundle.course.unitRequirements, 'id')
    return edited && edited.length
  } else {
    return false
  }
}

const isDraggable = bundle => {
  const draggable =
    !degreeStore.disableButtons
    && hasAssignedCourses.value
    && canEdit
    && bundle.course
    && !degreeStore.draggingContext.course
  return !!draggable
}

const isDroppable = category => {
  let droppable =
    !isCampusRequirements.value
    && category
    && !category.courses.length
    && category.id === degreeStore.draggingContext.target
  if (droppable) {
    const course = degreeStore.draggingContext.course
    const assignedCourses = getAssignedCourses(props.parentCategory, course.id)
    const courseKeys = map(assignedCourses, getCourseKey)
    droppable = course.categoryId === category.parentCategoryId || !includes(courseKeys, getCourseKey(course))
  }
  return droppable
}

const isEditing = bundle => {
  const isMatch = key => {
    const id = get(bundle, `${key}.id`)
    return id && (id === get(bundleForEdit.value, `${key}.id`))
  }
  return bundle.course ? isMatch('course') : isMatch('category')
}

const isNoteVisible = bundle => {
  return includes(notesVisible.value, bundle.key)
}

const isSatisfied = bundle => {
  return bundle.course || get(bundle.category, 'categoryType') === 'Campus Requirement, Satisfied'
}

const onDelete = bundle => {
  hoverCourseId.value = null
  degreeStore.setDisableButtons(true)
  bundleForDelete.value = bundle
  isDeleting.value = true
  alertScreenReader(`Delete ${bundle.name}`)
}

const onDrag = (event, stage, bundle) => {
  switch (stage) {
  case 'end':
    hoverCourseId.value = null
    degreeStore.draggingContextReset()
    break
  case 'enter':
  case 'over':
    event.stopPropagation()
    event.preventDefault()
    degreeStore.setDraggingTarget(bundle ? get(bundle.category, 'id') : emptyCategoryId)
    break
  case 'leave':
    degreeStore.setDraggingTarget(null)
    break
  case 'start':
    if (event.target) {
      // Required for Safari
      event.target.style.opacity = 0.9
    }
    degreeStore.dragStart(bundle.course, 'assigned')
    break
  case 'exit':
  default:
    break
  }
}

const onDropCourse = (event, category, context) => {
  event.stopPropagation()
  event.preventDefault()
  hoverCourseId.value = null
  if (isDroppable(category)) {
    onDrop(category, context)
  }
  degreeStore.setDraggingTarget(null)
  return false
}

const onMouse = (stage, bundle) => {
  if (isDraggable(bundle)) {
    switch(stage) {
    case 'enter':
      if (isDraggable(bundle)) {
        hoverCourseId.value = get(bundle.course, 'id')
      }
      break
    case 'leave':
      hoverCourseId.value = null
      break
    default:
      break
    }
  }
}

const showNote = bundle => {
  notesVisible.value.push(bundle.key)
  alertScreenReader(`Showing note of ${bundle.name}`)
}
</script>

<style scoped>
table {
  border-collapse: collapse;
  border-spacing: 0 0.05em;
}
.btn-container {
  min-width: 20px;
}
.changed-units-icon {
  color: #00c13a;
  margin-right: 0.3em;
}
.drop-zone-on {
  background-color: #ecf5fb;
  cursor: move;
  outline: #8bbdda dashed 0.15em;
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
.td-actions {
  padding: 0 4px 0 0;
  vertical-align: middle;
  width: 32px;
}
.td-course-assignment-menu {
  font-size: 14px;
  padding: 0 2px 0 5px;
  vertical-align: middle;
  width: 14px;
}
.td-grade {
  padding: 0 0.5em 0 0.4em;
  vertical-align: middle;
  width: 36px;
}
.td-name {
  padding: 0.25em 0 0.25em 0.25em;
  vertical-align: middle;
}
.td-name-printable {
  padding: 0.25em 0;
  vertical-align: middle;
  width: 180px !important;
}
.td-note {
  max-width: 100px;
  padding: 0 0.5em 0 0;
  vertical-align: middle;
  width: 1px;
}
.td-note-printable {
  padding: 0 0.5em 0 0;
  vertical-align: middle;
  width: 100px !important;
}
.td-max-width-0 {
  max-width: 0;
}
.td-satisfied {
  width: 50px;
}
.td-units {
  text-align: right;
  padding: 0 0.5em 0 0;
  vertical-align: middle;
  white-space: nowrap;
  width: 50px;
}
.th-course-assignment-menu {
  width: 14px;
}
.th-note {
  width: 100px;
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
.unit-requirement-count {
  background-color: #3b7ea5;
  border-radius: 12px;
  color: white;
  height: 20px;
  text-align: center;
  max-width: 20px;
  min-width: 20px;
}
</style>
