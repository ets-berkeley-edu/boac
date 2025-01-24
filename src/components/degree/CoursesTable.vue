<template>
  <div>
    <table
      :id="`column-${position}-courses-of-category-${parentCategory.id}`"
      class="mb-0 w-100"
    >
      <caption class="sr-only">{{ parentCategory.name }} Courses</caption>
      <thead class="border-b-md">
        <tr class="sortable-table-header text-no-wrap">
          <th v-if="hasAssignedCourses && canEdit" class="force-width-18">
            <span class="sr-only">{{ hasAssignedCourses ? 'Assign course' : 'Recommended?' }}</span>
          </th>
          <th v-if="!isCampusRequirements" class="font-size-11" :class="{'force-width-80': !isCampusRequirements}">Course</th>
          <th v-if="isCampusRequirements" class="font-size-11 w-40">Requirement</th>
          <th v-if="degreeStore.sid && !isCampusRequirements" class="font-size-11 force-width-24 truncate-with-ellipsis" title="Grade">Grade</th>
          <th v-if="!isCampusRequirements && items.length" class="font-size-11 pr-2 text-right force-width-24 truncate-with-ellipsis" title="Units">Units</th>
          <th v-if="degreeStore.sid && isCampusRequirements" class="font-size-11 force-width-42 pl-0 pr-2 text-center">Satisfied</th>
          <th v-if="degreeStore.sid" class="font-size-11 pl-0" :class="{'th-note': hasNotes, 'th-note-when-all-notes-empty': !hasNotes}">Note</th>
          <th v-if="!degreeStore.sid && !isCampusRequirements && items.length" class="font-size-11 th-fulfillment px-0">Fulfillment</th>
          <th v-if="canEdit && (degreeStore.sid || !isCampusRequirements)" class="font-size-11 th-actions px-0"><span class="sr-only">Actions</span></th>
        </tr>
      </thead>
      <tbody>
        <template v-for="(bundle, index) in categoryCourseBundles" :key="`tr-${index}`">
          <tr
            :id="`course-${bundle.category.id}-table-row-${index}`"
            :class="{
              'text-accent-blue': getAccentColor(bundle) === 'Blue',
              'text-accent-green': getAccentColor(bundle) === 'Green',
              'text-accent-orange': getAccentColor(bundle) === 'Orange',
              'text-accent-purple': getAccentColor(bundle) === 'Purple',
              'text-accent-red': getAccentColor(bundle) === 'Red',
              'border-e-md border-s-md border-t-md': isNoteVisible(bundle),
              'cursor-grab': isDraggable(bundle),
              'drop-zone-on': isDroppable(bundle.category),
              'mouseover-grabbable': bundle.course && hoverCourseId === bundle.course.id && !degreeStore.draggingContext.course,
              'tr-while-dragging': bundle.course && (degreeStore.draggingCourseId === get(bundle.course, 'id'))
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
            <td v-if="hasAssignedCourses && canEdit && !isCampusRequirements" class="force-width-18 td-assign">
              <div
                v-if="bundle.course && canEdit && (degreeStore.draggingCourseId !== bundle.course.id)"
                :id="`assign-course-${bundle.course.id}-menu-container`"
              >
                <CourseAssignmentMenu
                  v-if="bundle.course.categoryId"
                  :after-course-assignment="course => putFocusNextTick(`assign-course-${course.id}-btn`, {cssSelector: 'button'})"
                  :course="bundle.course"
                />
              </div>
            </td>
            <td
              class="force-width-80 overflow-wrap-break-word pl-0"
              :class="{
                'align-content-start': printable && getNote(bundle),
                'font-italic text-surface-variant': !isSatisfied(bundle) && !getAccentColor(bundle),
                'pl-2': isCampusRequirements && isNoteVisible(bundle),
                'td-name-printable': printable,
                'td-name': !printable,
                'text-no-wrap': isCampusRequirements,
                'vertical-top': !isCampusRequirements
              }"
            >
              <span v-if="!bundle.course && bundle.category.isRecommended">
                <v-icon
                  :id="`category-${bundle.category.id}-is-recommended`"
                  color="accent-orange"
                  :icon="mdiCircle"
                  title="Recommended"
                />
                <span class="sr-only">This is a recommended course requirement</span>
              </span>
              <span
                :class="{
                  'text-accent-purple': get(bundle.category, 'isSatisfiedByTransferCourse'),
                  'font-weight-500': isEditing(bundle),
                  'mr-2': get(bundle.course, 'isCopy')
                }"
              >
                <span :class="{'text-strikethrough': get(bundle.category, 'isIgnored'), 'demo-mode-blur': degreeStore.sid && bundle.type === 'course' && currentUser.inDemoMode}">
                  <!-- Spaces surrounding 'name' make life easier for QA. Do not trim. -->
                  {{ bundle.name }}
                </span>
              </span>
              <span v-if="get(bundle.course, 'isCopy')" class="mr-1">
                <v-icon
                  :icon="mdiContentCopy"
                  size="sm"
                  title="Course satisfies multiple requirements."
                />
              </span>
            </td>
            <td
              v-if="degreeStore.sid && !isCampusRequirements"
              class="td-grade"
              :class="{
                'force-width-24': isAlertGrade(getGrade(bundle)),
                'force-width-50': isAlertGrade(getGrade(bundle))
              }"
            >
              <div class="d-flex align-center">
                <span
                  :class="{
                    'font-italic text-surface-variant': !bundle.course && !getAccentColor(bundle),
                    'font-size-12': printable,
                    'font-size-14 text-no-wrap': !printable
                  }"
                >
                  {{ getGrade(bundle) }}
                </span>
                <v-icon
                  v-if="isAlertGrade(getGrade(bundle))"
                  class="ml-1"
                  color="warning"
                  :icon="mdiAlert"
                  size="20"
                  title="Non-passing grade"
                />
              </div>
            </td>
            <td
              v-if="!isCampusRequirements"
              class="td-units"
              :class="{'font-italic text-surface-variant': !bundle.course && !getAccentColor(bundle)}"
            >
              <div class="d-flex align-center justify-end">
                <v-icon
                  v-if="isCourseFulfillmentsEdited(bundle)"
                  class="mr-1"
                  color="accent-green"
                  :icon="mdiCheckCircleOutline"
                  size="18"
                  :title="bundle.course.unitRequirements.length ? `Counts towards ${oxfordJoin(getCourseFulfillments(bundle))}.` : 'Fulfills no unit requirements'"
                />
                <v-icon
                  v-if="unitsWereEdited(bundle.course)"
                  :id="`units-were-edited-${bundle.course.id}`"
                  class="changed-units-icon"
                  color="accent-green"
                  :icon="mdiInformation"
                  size="18"
                  :title="`Updated from ${pluralize('unit', bundle.course.sis.units)}`"
                />
                <div :class="{'font-size-12': printable, 'font-size-14': !printable}">{{ isNil(bundle.units) ? '&mdash;' : bundle.units }}</div>
                <span v-if="unitsWereEdited(bundle.course)" class="sr-only"> (updated from {{ pluralize('unit', bundle.course.sis.units) }})</span>
              </div>
            </td>
            <td v-if="degreeStore.sid && isCampusRequirements" class="td-satisfied float-right">
              <CampusRequirementCheckbox
                :campus-requirement="bundle"
                :position="position"
                :printable="printable"
              />
            </td>
            <td
              v-if="degreeStore.sid"
              :class="{
                'font-italic text-surface-variant': !isSatisfied(bundle) && !getAccentColor(bundle),
                'td-note-printable': printable,
                'td-note': !printable && hasNotes,
                'td-note-when-all-notes-empty': !printable && !hasNotes,
                'vertical-top': !isCampusRequirements
              }"
            >
              <div v-if="getNote(bundle)">
                <pre
                  v-if="printable"
                  :id="`column-${position}-${bundle.key}-note`"
                  class="font-size-12"
                  v-html="getNote(bundle)"
                />
                <div v-if="!printable && !isNoteVisible(bundle)" class="font-size-14 truncate-with-ellipsis">
                  <a
                    :id="`column-${position}-${bundle.key}-note`"
                    :aria-label="truncate(getNote(bundle), {length: 30, separator: ' '})"
                    :aria-controls="`column-${position}-${bundle.key}-full-note`"
                    :aria-expanded="isNoteVisible(bundle)"
                    href
                    role="button"
                    title="Expand note"
                    @click.prevent="showNote(bundle, position)"
                    v-html="getNote(bundle)"
                  />
                </div>
              </div>
              <div
                v-if="!getNote(bundle)"
                :id="`column-${position}-${bundle.key}-note`"
                class="font-size-14"
              >
                &mdash;
              </div>
            </td>
            <td
              v-if="!degreeStore.sid && !isCampusRequirements"
              class="vertical-top td-fulfillment"
              :class="{
                'font-italic text-surface-variant': !bundle.course && !getAccentColor(bundle),
                'font-size-12': printable,
                'font-size-14': !printable
              }"
              :title="oxfordJoin(map(bundle.unitRequirements, 'name'), 'None')"
            >
              <div v-if="size(bundle.unitRequirements)" class="align-items-start d-flex flex-row-reverse justify-end">
                <v-chip
                  v-if="size(bundle.unitRequirements) > 1"
                  class="d-flex justify-center unit-requirement-count font-weight-bold"
                  color="primary"
                  rounded="circle"
                  size="small"
                  variant="flat"
                >
                  <span :title="`Fulfills ${bundle.unitRequirements.length} Unit Requirements`">{{ bundle.unitRequirements.length }}</span>
                </v-chip>
                <div>
                  {{ oxfordJoin(map(bundle.unitRequirements, 'name'), '&mdash;') }}
                </div>
              </div>
            </td>
            <td
              v-if="canEdit && (degreeStore.sid || !isCampusRequirements)"
              :class="{
                'vertical-middle pb-1': degreeStore.sid,
                'pr-2': isCampusRequirements,
                'vertical-top': !isCampusRequirements
              }"
            >
              <div class="degree-check-action-buttons align-center d-flex text-no-wrap">
                <v-btn
                  v-if="!degreeStore.draggingCourseId || degreeStore.draggingCourseId !== get(bundle.course, 'id')"
                  :id="`column-${position}-edit-${bundle.key}-btn`"
                  :aria-label="`Edit ${bundle.name}`"
                  :class="{'bg-transparent text-primary': !degreeStore.disableButtons}"
                  density="compact"
                  :disabled="degreeStore.disableButtons"
                  flat
                  :icon="mdiNoteEditOutline"
                  size="small"
                  @click="edit(bundle, position)"
                />
                <v-btn
                  v-if="!degreeStore.sid || (bundle.course && (bundle.course.isCopy || bundle.course.manuallyCreatedBy)) && (degreeStore.draggingCourseId !== get(bundle.course, 'id'))"
                  :id="`column-${position}-delete-${bundle.key}-btn`"
                  :aria-label="`Delete ${bundle.name}`"
                  :class="{'bg-transparent text-primary': !degreeStore.disableButtons}"
                  density="compact"
                  :disabled="degreeStore.disableButtons"
                  flat
                  :icon="mdiTrashCan"
                  size="small"
                  @click="() => onDelete(bundle)"
                />
              </div>
            </td>
          </tr>
          <tr v-if="isEditing(bundle)" :key="`tr-${index}-edit`">
            <td
              :id="`column-${position}-${bundle.key}-edit`"
              :class="{'pb-3 pl-4 pt-1': bundle.course || !degreeStore.sid}"
              :colspan="columnCount"
            >
              <div class="border-md ma-2 px-4 py-2">
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
              </div>
            </td>
          </tr>
          <tr
            v-if="isNoteVisible(bundle)"
            :id="`column-${position}-${bundle.key}-full-note`"
            :key="`tr-${index}-note`"
            class="border-b-md border-e-md border-s-md"
          >
            <td :colspan="columnCount" class="pl-6 py-1">
              <div class="overflow-wrap-break-word">
                <pre
                  :id="bundle.course ? `course-${bundle.course.id}-note` : `category-${bundle.category.id}-note`"
                  aria-live="polite"
                  class="font-size-14"
                ><span class="sr-only">Note: </span><span v-html="getNote(bundle)" /></pre>
              </div>
              <div class="font-size-12 text-no-wrap">
                [<v-btn
                  :id="`column-${position}-${bundle.key}-hide-note-btn`"
                  :aria-controls="`column-${position}-${bundle.key}-full-note`"
                  :aria-expanded="true"
                  class="px-0 py-1 text-primary"
                  size="small"
                  text="Hide note"
                  variant="text"
                  @click="hideNote(bundle, position)"
                />]
              </div>
            </td>
          </tr>
        </template>
        <tr v-if="!items.length">
          <td class="pa-2" :class="{'pb-3': !degreeStore.sid}" :colspan="columnCount">
            <span
              :id="emptyCategoryId"
              class="font-italic text-surface-variant"
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
      <tfoot v-if="degreeStore.sid && canEdit && !isCampusRequirements">
        <tr>
          <td class="pb-5" :colspan="columnCount">
            <CreateCourseModal :parent-category="parentCategory" />
          </td>
        </tr>
      </tfoot>
    </table>
    <AreYouSureModal
      v-if="isDeleting"
      v-model="isDeleting"
      button-label-confirm="Delete"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      modal-header="Delete Course"
      :text="`Are you sure you want to delete <strong>&quot;${bundleForDelete.name}&quot;</strong>`"
    />
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
import {each, every, find, get, includes, isEmpty, isNil, map, remove, size, trim, truncate, xorBy} from 'lodash'
import {
  findCategoryById,
  getAssignedCourses,
  getCourseKey,
  isCampusRequirement,
  unitsWereEdited
} from '@/lib/degree-progress'
import {isAlertGrade} from '@/berkeley'
import {
  mdiAlert,
  mdiCheckCircleOutline,
  mdiCircle,
  mdiContentCopy,
  mdiInformation,
  mdiNoteEditOutline,
  mdiTrashCan
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

const columnCount = computed(() => {
  // See the logic in the `thead.th` elements to understand the calculation below.
  const hasItems = props.items.length
  const sid = degreeStore.sid
  let colspan = 1
  colspan += hasAssignedCourses.value && canEdit ? 1 : 0
  colspan += sid && !isCampusRequirements.value ? 1 : 0
  colspan += !isCampusRequirements.value && hasItems ? 1 : 0
  colspan += sid && isCampusRequirements.value ? 1 : 0
  colspan += sid ? 1 : 0
  colspan += !sid && !isCampusRequirements.value && hasItems ? 1 : 0
  colspan += canEdit && (sid || !isCampusRequirements.value) ? 1 : 0
  return colspan
})

const hasAssignedCourses = computed(() => {
  return !!find(categoryCourseBundles.value, bundle => bundle.course)
})

const hasNotes = computed(() => {
  return !!find(categoryCourseBundles.value, bundle => getNote(bundle))
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
  alertScreenReader(`Updated "${bundleForEdit.value.name}" ${bundleForEdit.value.type}`)
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
  const type = bundleForDelete.value.type
  const done = () => {
    alertScreenReader(`Deleted "${name}" ${type}.`)
    const putFocus = degreeStore.sid ? `column-${props.position}-add-course-to-category-${props.parentCategory.id}` : 'page-header'
    isDeleting.value = false
    bundleForDelete.value = null
    degreeStore.setDisableButtons(false)
    putFocusNextTick(putFocus)
  }
  alertScreenReader('Deleting')
  if (degreeStore.sid) {
    deleteCourse(bundleForDelete.value.course.id).then(done)
  } else {
    deleteCategory(bundleForDelete.value.category.id).then(done)
  }
}

const describeCategoryUnits = category => {
  if (category) {
    const showRange = category.unitsUpper && category.unitsLower !== category.unitsUpper
    return showRange ? `${category.unitsLower}-${category.unitsUpper}` : category.unitsLower
  } else {
    return null
  }
}

const edit = (bundle, position) => {
  hideNote(bundle, position, false)
  hoverCourseId.value = null
  degreeStore.setDisableButtons(true)
  bundleForEdit.value = bundle
  putFocusNextTick(`column-${position}-${bundle.key}-edit`, 'input,textarea,button')
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
const getNote = bundle => trim(bundle.course ? bundle.course.note : bundle.category.note)

const hideNote = (bundle, position, manageFocus=true) => {
  notesVisible.value = remove(notesVisible.value, key => bundle.key !== key)
  if (manageFocus) {
    putFocusNextTick(`column-${position}-${bundle.key}-note`)
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

const showNote = (bundle, position) => {
  notesVisible.value.push(bundle.key)
  putFocusNextTick(`column-${position}-${bundle.key}-hide-note-btn`)
}
</script>

<style scoped>
pre {
  padding-right: 5px;
  white-space: pre-wrap;
}
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
  margin-right: 0.3em;
}
.td-assign {
  font-size: 14px;
  vertical-align: top;
}
.td-fulfillment {
  word-break: break-word;
}
.td-grade {
  padding: 1px 0 0 0;
  text-transform: capitalize;
  vertical-align: top;
}
.td-name {
  font-size: 14px;
  padding: 1px 0 0 0;
}
.td-name-printable {
  font-size: 12px;
  padding: 0.25em 0;
  vertical-align: middle;
  width: 180px !important;
}
.td-note {
  padding: 1px 4px 0 4px;
}
.td-note-when-all-notes-empty {
  max-width: 10px;
}
.td-note-printable {
  padding: 0 0.5em 0 0;
  vertical-align: middle;
  width: 100px !important;
}
.td-satisfied {
  padding: 1px 0 0 0;
  width: 50px;
}
.td-units {
  padding: 0 8px 0 0;
  vertical-align: top;
  white-space: nowrap;
}
.th-actions {
  width: 36px !important;
}
.th-fulfillment {
  min-width: 72px !important;
  width: 35% !important;
}
.th-note {
  max-width: 25% !important;
  padding-left: 4px !important;
  width: 25% !important;
}
.th-note-when-all-notes-empty {
  max-width: 10px !important;
  width: 10px !important;
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
.unit-requirement-count {
  height: 20px;
  margin-top: 1px;
  max-width: 20px;
  min-width: 20px;
  width: 20px;
}
.text-strikethrough {
  text-decoration: line-through;
}
</style>
