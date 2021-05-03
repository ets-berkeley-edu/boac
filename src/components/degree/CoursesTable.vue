<template>
  <div>
    <div v-if="items.length">
      <b-table-simple
        :id="`column-${position}-courses-of-category-${parentCategory.id}`"
        borderless
        class="mb-0"
        small
      >
        <b-thead class="border-bottom">
          <b-tr class="sortable-table-header text-nowrap">
            <b-th v-if="allAddedCourses.length && $currentUser.canEditDegreeProgress"><span class="sr-only">Menu</span></b-th>
            <b-th class="pl-0 table-cell-course">Course</b-th>
            <b-th class="table-cell-units">Units</b-th>
            <b-th>Fulfillment</b-th>
            <b-th v-if="$currentUser.canEditDegreeProgress" class="sr-only">Actions</b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="(bundle, index) in categoryCourseBundles" :id="`course-${bundle.category.id}-table-row`" :key="index">
            <td v-if="allAddedCourses.length && $currentUser.canEditDegreeProgress" class="pt-0">
              <div v-if="!isEditing(bundle) && bundle.course && !bundle.course.isCopy">
                <CourseAssignmentMenu
                  v-if="bundle.course.categoryId"
                  :course="bundle.course"
                  :student="student"
                />
              </div>
            </td>
            <td
              v-if="!isEditing(bundle)"
              class="font-size-14 pl-0 pr-3 table-cell-course"
            >
              {{ bundle.name }}
            </td>
            <td
              v-if="!isEditing(bundle)"
              class="float-right font-size-14 pr-2 table-cell-units text-nowrap"
            >
              <span class="font-size-14">{{ bundle.units || '&mdash;' }}</span>
            </td>
            <td
              v-if="!isEditing(bundle)"
              class="font-size-14 td-max-width-0"
              :title="oxfordJoin($_.map(bundle.unitRequirements, 'name'), 'None')"
            >
              <div class="align-items-start d-flex justify-content-between">
                <div class="ellipsis-if-overflow">
                  {{ oxfordJoin($_.map(bundle.unitRequirements, 'name'), '&mdash;') }}
                </div>
                <div v-if="$_.size(bundle.unitRequirements) > 1" class="unit-requirement-count">
                  <span class="sr-only">(Has </span>{{ bundle.unitRequirements.length }}<span class="sr-only"> requirements.)</span>
                </div>
              </div>
            </td>
            <td v-if="$currentUser.canEditDegreeProgress && !isEditing(bundle) && isEditable(bundle)" class="pr-0 w-10">
              <div class="d-flex justify-content-end text-nowrap">
                <b-btn
                  :id="`column-${position}-edit-category-${bundle.category.id}-btn`"
                  class="pl-0 pt-0"
                  :class="{'pr-2': student}"
                  :disabled="disableButtons"
                  size="sm"
                  variant="link"
                  @click="edit(bundle)"
                >
                  <font-awesome icon="edit" />
                  <span class="sr-only">Edit {{ bundle.name }}</span>
                </b-btn>
                <b-btn
                  v-if="!student || (bundle.course && bundle.course.isCopy)"
                  :id="`column-${position}-delete-course-${bundle.category.id}-btn`"
                  class="px-0 pt-0"
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
            <b-td v-if="isEditing(bundle)" colspan="4">
              <EditCategory
                :after-cancel="afterCancel"
                :after-save="afterSave"
                :existing-category="bundle.category"
                :position="position"
              />
            </b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
    </div>
    <div class="mb-3 ml-1" :class="{'mt-2': !items.length}">
      <AddCourseToCategory
        :courses-already-added="allAddedCourses"
        :parent-category="parentCategory"
        :position="position"
        :student="student"
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
import Util from '@/mixins/Util'

export default {
  name: 'CoursesTable',
  mixins: [DegreeEditSession, Util],
  components: {AddCourseToCategory, CourseAssignmentMenu, EditCategory, AreYouSureModal},
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
    student: {
      default: undefined,
      required: false,
      type: Object
    }
  },
  data: () => ({
    bundleForDelete: undefined,
    bundleForEdit: undefined,
    isAddingCourse: false
  }),
  computed: {
    allAddedCourses() {
      const allCourses = []
      this.$_.each(this.categoryCourseBundles, bundle => {
        if (bundle.course) {
          allCourses.push(bundle.course)
        }
      })
      return allCourses
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
          units: (course || category).units,
          unitRequirements: (course || category).unitRequirements
        })
      })
      return transformed
    }
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
    edit(bundle) {
      this.setDisableButtons(true)
      this.$announcer.polite(`Edit ${bundle.name}`)
      this.bundleForEdit = bundle
      this.putFocusNextTick(`column-${this.position}-name-input`)
    },
    isEditable(bundle) {
      // The row is editable if (1) it has course assignment/copy, or (2) this is a degree template, not a degree check.
      return bundle.course || !this.student
    },
    isEditing(bundle) {
      return this.$_.get(bundle, 'category.id') === this.$_.get(this.bundleForEdit, 'category.id')
    }
  }
}
</script>

<style scoped>
.ellipsis-if-overflow {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.table-cell-course {
  min-width: 150px !important;
  width: 1px;
}
.table-cell-units {
  direction: rtl;
  max-width: 10px !important;
  min-width: 10px !important;
}
.td-max-width-0 {
  max-width: 0;
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
