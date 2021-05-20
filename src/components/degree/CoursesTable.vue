<template>
  <div>
    <div>
      <b-table-simple
        :id="`column-${position}-courses-of-category-${parentCategory.id}`"
        borderless
        class="mb-0"
        small
      >
        <b-thead class="border-bottom">
          <b-tr class="sortable-table-header text-nowrap">
            <b-th v-if="assignedCourseCount && $currentUser.canEditDegreeProgress" class="th-course-assignment-menu">
              <span class="sr-only">Options to re-assign course</span>
            </b-th>
            <b-th class="pl-0">Course</b-th>
            <b-th class="pl-0 text-right">Units</b-th>
            <b-th v-if="sid">Grade</b-th>
            <b-th v-if="sid">Note</b-th>
            <b-th v-if="!sid" class="px-0">Fulfillment</b-th>
            <b-th v-if="$currentUser.canEditDegreeProgress" class="px-0 sr-only">Actions</b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <template v-for="(bundle, index) in categoryCourseBundles">
            <b-tr
              :id="`course-${bundle.category.id}-table-row-${index}`"
              :key="`tr-${index}`"
              :class="{
                'tr-while-dragging': bundle.course && isUserDragging(bundle.course.id),
                'drop-zone-on': isDroppable(bundle.category) && draggingOverCategoryId === bundle.category.id,
                'drop-zone-off': !bundle.category || bundle.category.courseIds.length || !isDroppable(bundle.category) || draggingOverCategoryId !== bundle.category.id
              }"
              :draggable="isDraggable(bundle)"
              @dragend="onDrag($event, 'end', bundle)"
              @dragenter="onDrag($event, 'enter', bundle)"
              @dragleave="onDrag($event, 'leave', bundle)"
              @dragover="onDrag($event, 'over', bundle)"
              @dragstart="onDrag($event, 'start', bundle)"
              @drop="onDropToCourseRequirement(bundle.category)"
            >
              <td v-if="assignedCourseCount && $currentUser.canEditDegreeProgress" class="td-course-assignment-menu">
                <div v-if="bundle.course && !bundle.course.isCopy && !isUserDragging(bundle.course.id)">
                  <CourseAssignmentMenu
                    v-if="bundle.course.categoryId"
                    :course="bundle.course"
                  />
                </div>
              </td>
              <td class="td-name" :class="{'faint-text font-italic': !bundle.course}">
                <span :class="{'font-weight-500': isEditing(bundle)}">{{ bundle.name }}</span>
              </td>
              <td class="td-units" :class="{'faint-text font-italic': !bundle.course}">
                <font-awesome
                  v-if="getCourseFulfillments(bundle).length"
                  class="fulfillments-icon mr-1"
                  icon="check-circle"
                  size="sm"
                  :title="`Counts towards ${oxfordJoin(getCourseFulfillments(bundle))}.`"
                />
                <font-awesome
                  v-if="isUnitDiff(bundle)"
                  class="changed-units-icon mr-1"
                  icon="info-circle"
                  size="sm"
                  :title="`Updated from ${pluralize('unit', bundle.category.unitsLower)}`"
                />
                <span class="font-size-14">{{ bundle.units || '&mdash;' }}</span>
                <span v-if="isUnitDiff(bundle)" class="sr-only"> (updated from {{ pluralize('unit', bundle.category.unitsLower) }})</span>
              </td>
              <td v-if="sid" class="td-grade">
                <span class="font-size-14 text-nowrap">
                  {{ $_.get(bundle.course, 'grade') }}
                </span>
              </td>
              <td v-if="sid" class="ellipsis-if-overflow td-note" :title="$_.get(bundle.course, 'note')">
                <span class="font-size-14">
                  {{ $_.get(bundle.course, 'note') }}
                </span>
              </td>
              <td
                v-if="!sid"
                class="align-middle font-size-14 td-max-width-0"
                :class="{'faint-text font-italic': !bundle.course}"
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
              <td v-if="$currentUser.canEditDegreeProgress" class="td-actions">
                <div v-if="isEditable(bundle) && !isUserDragging($_.get(bundle.course, 'id'))" class="d-flex justify-content-end text-nowrap">
                  <b-btn
                    v-if="!sid"
                    :id="`column-${position}-edit-category-${bundle.category.id}-btn`"
                    class="p-0"
                    :class="{'pr-0': sid && !$_.get(bundle.course, 'isCopy'), 'pr-1': !sid || (bundle.course && bundle.course.isCopy)}"
                    :disabled="disableButtons"
                    size="sm"
                    variant="link"
                    @click="edit(bundle)"
                  >
                    <font-awesome icon="edit" />
                    <span class="sr-only">Edit {{ bundle.name }}</span>
                  </b-btn>
                  <b-btn
                    v-if="!sid || (bundle.course && bundle.course.isCopy)"
                    :id="`column-${position}-delete-course-${bundle.category.id}-btn`"
                    class="p-0"
                    :disabled="disableButtons"
                    size="sm"
                    variant="link"
                    @click="deleteCourse(bundle)"
                  >
                    <font-awesome icon="trash-alt" />
                    <span class="sr-only">Delete {{ bundle.name }}</span>
                  </b-btn>
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
                  v-if="!bundle.course"
                  :after-cancel="afterCancel"
                  :after-save="afterSave"
                  :existing-category="bundle.category"
                  :position="position"
                />
              </b-td>
            </b-tr>
          </template>
          <b-tr
            v-if="!items.length"
            :class="{'drop-zone-on': draggingOverCategoryId === -1}"
            @dragenter="onDrag($event, 'enter')"
            @dragleave="onDrag($event, 'leave')"
            @dragover="onDrag($event, 'over')"
            @drop="onDropEmptyTable"
          >
            <b-td class="p-2" :class="{'pb-3': !sid}" colspan="5">
              <span class="faint-text font-italic font-size-16">No completed requirements</span>
            </b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
    </div>
    <div v-if="sid" class="mb-3" :class="{'mt-1': !items.length}">
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
import Util from '@/mixins/Util'

export default {
  name: 'CoursesTable',
  mixins: [DegreeEditSession, Util],
  components: {AddCourseToCategory, AreYouSureModal, CourseAssignmentMenu, EditCategory, EditCourse},
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
    }
  },
  data: () => ({
    bundleForDelete: undefined,
    bundleForEdit: undefined,
    draggingOverCategoryId: null
  }),
  computed: {
    allCourses() {
      const bundles = this.$_.filter(this.categoryCourseBundles, b => !!b.course)
      return this.$_.map(bundles, b => b.course)
    },
    assignedCourseCount() {
      let count = 0
      this.$_.each(this.categoryCourseBundles, bundle => bundle.course && !bundle.course.isCopy && count++)
      return count
    },
    categoryCourseBundles() {
      const transformed = []
      this.$_.each(this.items, item => {
        let category
        let course
        if (item.categoryType) {
          category = item
          course = category.courseIds.length ? this.getCourse(category.courseIds[0]) : null
        } else {
          course = item
          category = this.findCategoryById(course.categoryId)
        }
        transformed.push({
          category,
          course,
          name: (course || category).name,
          units: course ? course.units : this.describeCategoryUnits(category),
          unitRequirements: (course || category).unitRequirements
        })
      })
      return transformed
    }
  },
  created() {
    this.$eventHub.on('degree-progress-drag-end', () => {
      this.draggingOverCategoryId = null
    })
  },
  methods: {
    afterCancel() {
      this.$announcer.polite('Cancelled')
      this.putFocusNextTick(`column-${this.position}-edit-category-${this.bundleForEdit.category.id}-btn`)
      this.bundleForEdit = null
      this.setDisableButtons(false)
    },
    afterSave() {
      this.$announcer.polite(`Updated course ${this.bundleForEdit.name}`)
      this.putFocusNextTick(`column-${this.position}-edit-category-${this.bundleForEdit.category.id}-btn`)
      this.bundleForEdit = null
      this.setDisableButtons(false)
    },
    deleteCanceled() {
      this.putFocusNextTick(`column-${this.position}-delete-course-${this.bundleForDelete.category.id}-btn`)
      this.bundleForDelete = null
      this.$announcer.polite('Canceled. Nothing deleted.')
      this.setDisableButtons(false)
    },
    deleteConfirmed() {
      this.deleteCategory(this.bundleForDelete.category.id).then(() => {
        this.$announcer.polite(`${this.bundleForDelete.name} deleted.`)
        this.bundleForDelete = null
        this.setDisableButtons(false)
        this.putFocusNextTick('page-header')
      })
    },
    deleteCourse(bundle) {
      this.setDisableButtons(true)
      this.bundleForDelete = bundle
      this.$announcer.polite(`Delete ${bundle.name}`)
    },
    describeCategoryUnits(category) {
      if (category) {
        const showRange = category.unitsUpper && category.unitsLower !== category.unitsUpper
        return showRange ? `${category.unitsLower}-${category.unitsUpper}` : category.unitsLower
      } else {
        return null
      }
    },
    onDrag(event, stage, bundle) {
      switch (stage) {
      case 'end':
        this.draggingOverCategoryId = null
        this.onDragEnd()
        break
      case 'enter':
      case 'over':
        this.draggingOverCategoryId = bundle ? this.$_.get(bundle.category, 'id') : -1
        event.preventDefault()
        break
      case 'leave':
        this.draggingOverCategoryId = null
        break
      case 'start':
        this.onDragStart({courseId: bundle.course.id, dragContext: 'assigned'})
        break
      case 'exit':
      default:
        break
      }
    },
    edit(bundle) {
      this.setDisableButtons(true)
      this.$announcer.polite(`Edit ${bundle.name}`)
      this.bundleForEdit = bundle
      this.putFocusNextTick(`column-${this.position}-name-input`)
    },
    getCourseFulfillments(bundle) {
      if (bundle.category && bundle.course) {
        const categoryIds = this.$_.map(bundle.category.unitRequirements, 'id')
        const courseIds = this.$_.map(bundle.course.unitRequirements, 'id')
        const intersection = categoryIds.filter(id => courseIds.includes(id))
        return this.$_.map(this.$_.filter(bundle.category.unitRequirements, u => intersection.includes(u.id)), 'name')
      } else {
        return []
      }
    },
    isDraggable(bundle) {
      const draggable =
        !this.disableButtons
        && this.assignedCourseCount
        && this.$currentUser.canEditDegreeProgress
        && bundle.course
        && !bundle.course.isCopy
      return !!draggable
    },
    isDroppable(category) {
      return category
        && this.draggingOverCategoryId
        && !category.courseIds.length
        && category.id === this.draggingOverCategoryId
    },
    isEditable(bundle) {
      // The row is editable if (1) it has course assignment/copy, or (2) this is a degree template, not a degree check.
      return bundle.course || !this.sid
    },
    isEditing(bundle) {
      const isMatch = key => {
        const id = this.$_.get(bundle, `${key}.id`)
        return id && (id === this.$_.get(this.bundleForEdit, `${key}.id`))
      }
      return isMatch('category') || isMatch('course')
    },
    isUnitDiff(bundle) {
      return this.$_.get(bundle.course, 'isCopy') && bundle.course.units !== bundle.category.unitsLower
    },
    onDropToCourseRequirement(category) {
      this.onDrop({category: category, context: 'requirement'})
      this.draggingOverCategoryId = null
      return false
    },
    onDropEmptyTable(event) {
      event.preventDefault()
      this.onDrop({category: this.parentCategory, context: 'assigned'})
    }
  }
}
</script>

<style scoped>
table {
  border-collapse: separate;
  border-spacing: 0 0.05em;
}
.tr-while-dragging td:first-child,
th:first-child {
  border-radius: 10px 0 0 10px;
}
.tr-while-dragging td:last-child,
th:last-child {
  border-radius: 0 10px 10px 0;
}
.changed-units-icon {
  color: #00c13a;
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
.td-actions {
  padding: 0 4px 0 0;
  vertical-align: middle;
  width: 32px;
}
.th-course-assignment-menu {
  width: 14px;
}
.td-course-assignment-menu {
  font-size: 14px;
  padding: 0;
  vertical-align: middle;
  width: 14px;
}
.td-grade {
  padding: 0 0.5em 0 0.4em;
  vertical-align: middle;
  width: 50px;
}
.td-name {
  font-size: 14px;
  padding: 0.25em 0 0.25em 0.25em;
  vertical-align: middle;
}
.td-note {
  max-width: 60px;
  width: 1px;
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
