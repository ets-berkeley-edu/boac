<template>
  <div>
    <div>
      <b-table-simple
        :id="`column-${position}-courses-of-category-${parentCategory.id}`"
        :borderless="!printable"
        class="mb-0"
        small
      >
        <b-thead class="border-bottom">
          <b-tr class="sortable-table-header text-nowrap">
            <b-th v-if="(hasAssignedCourses && canEdit) || hasRecommended" class="th-course-assignment-menu">
              <span v-if="hasAssignedCourses" class="sr-only">Options to re-assign course</span>
              <span v-if="!hasAssignedCourses" class="sr-only">Recommended?</span>
            </b-th>
            <b-th class="pl-0" :class="{'font-size-12': printable}">Course</b-th>
            <b-th class="pl-0 text-right" :class="{'font-size-12': printable}">Units</b-th>
            <b-th v-if="sid" :class="{'font-size-12': printable}">Grade</b-th>
            <b-th v-if="sid" :class="{'font-size-12': printable}">Note</b-th>
            <b-th v-if="!sid" class="px-0" :class="{'font-size-12': printable}">Fulfillment</b-th>
            <b-th v-if="canEdit" class="px-0 sr-only">Actions</b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <template v-for="(bundle, index) in categoryCourseBundles">
            <b-tr
              :id="`course-${bundle.category.id}-table-row-${index}`"
              :key="`tr-${index}`"
              :class="{
                'accent-color-blue': $_.get(bundle, 'course.accentColor') === 'Blue',
                'accent-color-green': $_.get(bundle, 'course.accentColor') === 'Green',
                'accent-color-orange': $_.get(bundle, 'course.accentColor') === 'Orange',
                'accent-color-purple': $_.get(bundle, 'course.accentColor') === 'Purple',
                'accent-color-red': $_.get(bundle, 'course.accentColor') === 'Red',
                'cursor-grab': isDraggable(bundle),
                'drop-zone-on': isDroppable(bundle.category),
                'mouseover-grabbable': bundle.course && hoverCourseId === bundle.course.id && !draggingContext.course,
                'tr-while-dragging': bundle.course && isUserDragging(bundle.course.id)
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
              <td v-if="(hasAssignedCourses && canEdit) || hasRecommended" class="td-course-assignment-menu pt-1">
                <div
                  v-if="bundle.course && canEdit && !isUserDragging(bundle.course.id)"
                  :id="`assign-course-${bundle.course.id}-menu-container`"
                >
                  <CourseAssignmentMenu
                    v-if="bundle.course.categoryId"
                    :course="bundle.course"
                  />
                </div>
                <div v-if="!bundle.course && bundle.category.isRecommended">
                  <font-awesome
                    :id="`category-${bundle.category.id}-is-recommended`"
                    class="accent-color-orange"
                    icon="circle"
                    title="Recommended"
                  />
                  <span class="sr-only">This is a recommended course requirement</span>
                </div>
              </td>
              <td
                class="td-name"
                :class="{
                  'faint-text font-italic': !bundle.course,
                  'font-size-12': printable,
                  'font-size-14': !printable
                }"
              >
                <div class="align-items-center d-flex pt-1">
                  <div
                    :class="{
                      'font-weight-500': isEditing(bundle),
                      'pr-2': $_.get(bundle.course, 'isCopy')
                    }"
                  >
                    {{ bundle.name }}
                  </div>
                  <div v-if="$_.get(bundle.course, 'isCopy') && !printable" class="pr-1">
                    <font-awesome
                      icon="copy"
                      size="sm"
                      title="Course satisfies multiple requirements."
                    />
                  </div>
                </div>
              </td>
              <td class="td-units" :class="{'faint-text font-italic': !bundle.course}">
                <font-awesome
                  v-if="isCourseFulfillmentsEdited(bundle) && !printable"
                  class="fulfillments-icon mr-1"
                  icon="check-circle"
                  size="sm"
                  :title="bundle.course.unitRequirements.length ? `Counts towards ${oxfordJoin(getCourseFulfillments(bundle))}.` : 'Fulfills no unit requirements'"
                />
                <font-awesome
                  v-if="unitsWereEdited(bundle.course) && !printable"
                  :id="`units-were-edited-${bundle.course.id}`"
                  class="changed-units-icon"
                  icon="info-circle"
                  size="sm"
                  :title="`Updated from ${pluralize('unit', bundle.course.sis.units)}`"
                />
                <span :class="{'font-size-12': printable, 'font-size-14': !printable}">{{ $_.isNil(bundle.units) ? '&mdash;' : bundle.units }}</span>
                <span v-if="unitsWereEdited(bundle.course)" class="sr-only"> (updated from {{ pluralize('unit', bundle.course.sis.units) }})</span>
              </td>
              <td v-if="sid" class="td-grade">
                <span :class="{'font-size-12': printable, 'font-size-14 text-nowrap': !printable}">
                  {{ $_.get(bundle.course, 'grade') }}
                </span>
              </td>
              <td
                v-if="sid"
                :class="{'td-note-printable': printable, 'ellipsis-if-overflow td-note': !printable}"
                :title="$_.get(bundle.course, 'note')"
              >
                <span :class="{'font-size-12': printable, 'font-size-14': !printable}">
                  {{ $_.get(bundle.course, 'note') }}
                </span>
              </td>
              <td
                v-if="!sid"
                class="align-middle td-max-width-0"
                :class="{
                  'faint-text font-italic': !bundle.course,
                  'font-size-12': printable,
                  'font-size-14': !printable
                }"
                :title="oxfordJoin($_.map(bundle.unitRequirements, 'name'), 'None')"
              >
                <div class="align-items-start d-flex justify-content-between">
                  <div class="ellipsis-if-overflow">
                    <span>
                      {{ oxfordJoin($_.map(bundle.unitRequirements, 'name'), '&mdash;') }}
                    </span>
                  </div>
                  <div v-if="$_.size(bundle.unitRequirements) > 1" class="unit-requirement-count">
                    <span class="sr-only">(Has </span>{{ bundle.unitRequirements.length }}<span class="sr-only"> requirements.)</span>
                  </div>
                </div>
              </td>
              <td v-if="canEdit" class="td-actions">
                <div
                  v-if="isEditable(bundle)"
                  class="d-flex justify-content-end text-nowrap"
                >
                  <div class="btn-container">
                    <b-btn
                      v-if="!isUserDragging($_.get(bundle.course, 'id'))"
                      :id="`column-${position}-edit-${bundle.key}-btn`"
                      class="pl-0 pr-1 py-0"
                      :disabled="disableButtons"
                      size="sm"
                      variant="link"
                      @click="edit(bundle)"
                    >
                      <font-awesome icon="edit" />
                      <span class="sr-only">Edit {{ bundle.name }}</span>
                    </b-btn>
                  </div>
                  <div class="btn-container">
                    <b-btn
                      v-if="!sid || (bundle.course && (bundle.course.isCopy || bundle.course.manuallyCreatedBy)) && !isUserDragging($_.get(bundle.course, 'id'))"
                      :id="`column-${position}-delete-${bundle.key}-btn`"
                      class="pl-0 pr-1 py-0"
                      :disabled="disableButtons"
                      size="sm"
                      variant="link"
                      @click="onDelete(bundle)"
                    >
                      <font-awesome icon="trash-alt" />
                      <span class="sr-only">Delete {{ bundle.name }}</span>
                    </b-btn>
                  </div>
                </div>
              </td>
            </b-tr>
            <b-tr v-if="isEditing(bundle)" :key="`tr-${index}-edit`">
              <b-td class="p-0" colspan="6">
                <EditCourse
                  v-if="bundle.course"
                  :after-cancel="afterCancel"
                  :after-save="afterSave"
                  :course="bundle.course"
                  :position="position"
                />
                <EditCategory
                  v-if="!bundle.course && !sid"
                  :after-cancel="afterCancel"
                  :after-save="afterSave"
                  :existing-category="bundle.category"
                  :position="position"
                />
                <EditCourseRequirement
                  v-if="!bundle.course && sid"
                  :after-cancel="afterCancel"
                  :after-save="afterSave"
                  :category="bundle.category"
                  :position="position"
                />
              </b-td>
            </b-tr>
          </template>
          <b-tr v-if="!items.length">
            <b-td class="p-2" :class="{'pb-3': !sid}" colspan="5">
              <span
                :id="emptyCategoryId"
                class="faint-text font-italic"
                :class="{'font-size-14': printable, 'font-size-16': !printable}"
              >
                No completed requirements
              </span>
            </b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
    </div>
    <div v-if="sid && canEdit" class="mb-3" :class="{'mt-1': !items.length}">
      <AddCourseToCategory
        :courses-already-added="allCourses"
        :parent-category="parentCategory"
        :position="position"
      />
    </div>
    <AreYouSureModal
      v-if="bundleForDelete"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :modal-body="`Are you sure you want to delete <strong>&quot;${bundleForDelete.name}&quot;</strong>`"
      :show-modal="!!bundleForDelete"
      button-label-confirm="Delete"
      modal-header="Delete Course"
    />
  </div>
</template>

<script>
import AddCourseToCategory from '@/components/degree/student/AddCourseToCategory'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import CourseAssignmentMenu from '@/components/degree/student/CourseAssignmentMenu'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import EditCategory from '@/components/degree/EditCategory'
import EditCourse from '@/components/degree/student/EditCourse'
import EditCourseRequirement from '@/components/degree/student/EditCourseRequirement'
import Util from '@/mixins/Util'

export default {
  name: 'CoursesTable',
  mixins: [DegreeEditSession, Util],
  components: {
    AddCourseToCategory,
    AreYouSureModal,
    CourseAssignmentMenu,
    EditCategory,
    EditCourse,
    EditCourseRequirement
  },
  props: {
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
  },
  data: () => ({
    bundleForDelete: undefined,
    bundleForEdit: undefined,
    canEdit: undefined,
    emptyCategoryId: undefined,
    hoverCourseId: undefined
  }),
  computed: {
    allCourses() {
      const bundles = this.$_.filter(this.categoryCourseBundles, b => !!b.course)
      return this.$_.map(bundles, b => b.course)
    },
    categoryCourseBundles() {
      const transformed = []
      this.$_.each(this.items, item => {
        let category
        let course
        if (item.categoryType) {
          category = item
          course = category.courses.length ? this.getCourse(category.courses[0].id) : null
        } else {
          course = item
          category = this.findCategoryById(course.categoryId)
        }
        transformed.push({
          category,
          course,
          key: course ? `course-${course.id}` : `category-${category.id}`,
          name: this.getBundleName(course, category),
          units: course ? course.units : this.describeCategoryUnits(category),
          unitRequirements: (course || category).unitRequirements
        })
      })
      return transformed
    },
    hasAssignedCourses() {
      return !!this.$_.find(this.categoryCourseBundles, bundle => bundle.course)
    },
    hasRecommended() {
      return !!this.$_.find(this.categoryCourseBundles, bundle => {
        return !bundle.course && bundle.category.isRecommended
      })
    }
  },
  created() {
    this.canEdit = this.$currentUser.canEditDegreeProgress && !this.printable
    this.emptyCategoryId = `empty-category-${this.parentCategory.id}`
  },
  methods: {
    afterCancel() {
      this.$announcer.polite('Cancelled')
      this.$putFocusNextTick(`column-${this.position}-edit-${this.bundleForEdit.key}-btn`)
      this.bundleForEdit = null
      this.setDisableButtons(false)
    },
    afterSave() {
      this.$announcer.polite(`Updated ${this.bundleForEdit.key} ${this.bundleForEdit.name}`)
      this.$putFocusNextTick(`column-${this.position}-edit-${this.bundleForEdit.key}-btn`)
      this.bundleForEdit = null
      this.setDisableButtons(false)
    },
    deleteCanceled() {
      this.$putFocusNextTick(`column-${this.position}-delete-${this.bundleForDelete.key}-btn`)
      this.bundleForDelete = null
      this.$announcer.polite('Canceled. Nothing deleted.')
      this.setDisableButtons(false)
    },
    deleteConfirmed() {
      const name = this.bundleForDelete.name
      const done = () => {
        this.$announcer.polite(`${name} deleted.`)
        const putFocus = this.sid ? `column-${this.position}-add-course-to-category-${this.parentCategory.id}` : 'page-header'
        this.bundleForDelete = null
        this.setDisableButtons(false)
        this.$putFocusNextTick(putFocus)
      }
      let promise = undefined
      if (this.sid) {
        promise = this.deleteCourse(this.bundleForDelete.course.id).then(done)
      } else {
        promise = this.deleteCategory(this.bundleForDelete.category.id).then(done)
      }
      return promise
    },
    describeCategoryUnits(category) {
      if (category) {
        const showRange = category.unitsUpper && category.unitsLower !== category.unitsUpper
        return showRange ? `${category.unitsLower}-${category.unitsUpper}` : category.unitsLower
      } else {
        return null
      }
    },
    edit(bundle) {
      this.hoverCourseId = null
      this.setDisableButtons(true)
      this.$announcer.polite(`Edit ${bundle.name}`)
      this.bundleForEdit = bundle
    },
    getBundleName(course, category) {
      let name = (course || category).name
      if (course && this.printable) {
        this.$_.each(['COL', 'DIS', 'FLD', 'GRP', 'IND', 'LAB', 'LEC', 'SEM'], format => {
          const trimmed = name.replace(new RegExp(` ${format} [0-9]+$`), '')
          if (trimmed !== name) {
            name = trimmed
            return false
          }
        })
      }
      return name
    },
    getCourseFulfillments(bundle) {
      return bundle.course ? this.$_.map(bundle.course.unitRequirements, 'name') : []
    },
    isCourseFulfillmentsEdited(bundle) {
      if (bundle.category && bundle.course) {
        const edited = this.$_.xorBy(bundle.category.unitRequirements, bundle.course.unitRequirements, 'id')
        return edited && edited.length
      } else {
        return false
      }
    },
    isDraggable(bundle) {
      const draggable =
        !this.disableButtons
        && this.hasAssignedCourses
        && this.canEdit
        && bundle.course
        && !this.draggingContext.course
      return !!draggable
    },
    isDroppable(category) {
      let droppable = category && !category.courses.length && category.id === this.draggingContext.target
      if (droppable) {
        const course = this.draggingContext.course
        const assignedCourses = this.getAssignedCourses(this.parentCategory, course.id)
        const courseKeys = this.$_.map(assignedCourses, this.getCourseKey)
        droppable = course.categoryId === category.parentCategoryId || !this.$_.includes(courseKeys, this.getCourseKey(course))
      }
      return droppable
    },
    isEditable(bundle) {
      return bundle.course || bundle.category.isRecommended || !this.sid
    },
    isEditing(bundle) {
      const isMatch = key => {
        const id = this.$_.get(bundle, `${key}.id`)
        return id && (id === this.$_.get(this.bundleForEdit, `${key}.id`))
      }
      return bundle.course ? isMatch('course') : isMatch('category')
    },
    onDelete(bundle) {
      this.hoverCourseId = null
      this.setDisableButtons(true)
      this.bundleForDelete = bundle
      this.$announcer.polite(`Delete ${bundle.name}`)
    },
    onDrag(event, stage, bundle) {
      switch (stage) {
      case 'end':
        this.hoverCourseId = null
        this.onDragEnd()
        break
      case 'enter':
      case 'over':
        event.stopPropagation()
        event.preventDefault()
        this.setDraggingTarget(bundle ? this.$_.get(bundle.category, 'id') : this.emptyCategoryId)
        break
      case 'leave':
        this.setDraggingTarget(null)
        break
      case 'start':
        if (event.target) {
          // Required for Safari
          event.target.style.opacity = 0.9
        }
        this.onDragStart({course: bundle.course, dragContext: 'assigned'})
        break
      case 'exit':
      default:
        break
      }
    },
    onDropCourse(event, category, context) {
      event.stopPropagation()
      event.preventDefault()
      this.hoverCourseId = null
      if (this.isDroppable(category)) {
        this.onDrop({category, context})
      }
      this.setDraggingTarget(null)
      return false
    },
    onMouse(stage, bundle) {
      if (this.isDraggable(bundle)) {
        switch(stage) {
        case 'enter':
          if (this.isDraggable(bundle)) {
            this.hoverCourseId = this.$_.get(bundle.course, 'id')
          }
          break
        case 'leave':
          this.hoverCourseId = null
          break
        default:
          break
        }
      }
    }
  }
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
.drop-zone-on {
  background-color: #ecf5fb;
  cursor: move;
  outline: #8bbdda dashed 0.15em;
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
  width: 50px;
}
.td-name {
  padding: 0.25em 0 0.25em 0.25em;
  vertical-align: middle;
}
.td-note {
  max-width: 60px;
  padding: 0 0.5em 0 0;
  vertical-align: middle;
  width: 1px;
}
.td-note-printable {
  max-width: 60px;
  padding: 0 0.5em 0 0;
  vertical-align: middle;
}
.td-max-width-0 {
  max-width: 0;
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
