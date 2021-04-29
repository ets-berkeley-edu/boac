<template>
  <div>
    <div v-if="$_.isEmpty(items)" class="no-data-text">
      No courses
    </div>
    <div v-if="!$_.isEmpty(items)">
      <b-table-simple
        :id="`column-${position}-courses-of-category-${category.id}`"
        borderless
        small
      >
        <b-thead class="border-bottom">
          <b-tr class="sortable-table-header text-nowrap">
            <b-th v-if="hasFulfillments && $currentUser.canEditDegreeProgress"><span class="sr-only">Menu</span></b-th>
            <b-th class="pl-0 table-cell-course">Course</b-th>
            <b-th class="table-cell-units">Units</b-th>
            <b-th>Fulfillment</b-th>
            <b-th v-if="$currentUser.canEditDegreeProgress" class="sr-only">Actions</b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="(item, index) in items" :id="`course-${item.id}-table-row`" :key="index">
            <td v-if="hasFulfillments && $currentUser.canEditDegreeProgress" class="pt-0">
              <div v-if="!isEditing(item) && (!isCourseRequirement(item) || item.fulfilledBy.length)">
                <CourseAssignmentMenu
                  v-if="inspect(item, 'categoryId')"
                  :course="isCourseRequirement(item) ? item.fulfilledBy[0] : item"
                  :student="student"
                />
              </div>
            </td>
            <td
              v-if="!isEditing(item)"
              class="font-size-14 pl-0 pr-3 table-cell-course"
            >
              {{ inspect(item, 'name') }}
            </td>
            <td
              v-if="!isEditing(item)"
              class="float-right font-size-14 pr-2 table-cell-units text-nowrap"
            >
              <span class="font-size-14">{{ inspect(item, 'units') || '&mdash;' }}</span>
            </td>
            <td
              v-if="!isEditing(item)"
              class="font-size-14 td-max-width-0"
              :title="oxfordJoin($_.map(item.unitRequirements, 'name'), 'None')"
            >
              <div class="align-items-start d-flex justify-content-between">
                <div class="ellipsis-if-overflow">
                  {{ oxfordJoin($_.map(item.unitRequirements, 'name'), '&mdash;') }}
                </div>
                <div v-if="$_.size(item.unitRequirements) > 1" class="unit-requirement-count">
                  <span class="sr-only">(Has </span>{{ item.unitRequirements.length }}<span class="sr-only"> requirements.)</span>
                </div>
              </div>
            </td>
            <td v-if="$currentUser.canEditDegreeProgress && !isEditing(item)" class="pr-0 w-10">
              <div class="d-flex justify-content-end text-nowrap">
                <b-btn
                  :id="`column-${position}-edit-category-${item.id}-btn`"
                  class="pl-0 pt-0"
                  :class="{'pr-2': student}"
                  :disabled="disableButtons"
                  size="sm"
                  variant="link"
                  @click="edit(item)"
                >
                  <font-awesome icon="edit" />
                  <span class="sr-only">Edit {{ item.name }}</span>
                </b-btn>
                <b-btn
                  v-if="!student"
                  :id="`column-${position}-delete-course-${item.id}-btn`"
                  class="px-0 pt-0"
                  :disabled="disableButtons"
                  size="sm"
                  variant="link"
                  @click="deleteCourse(item)"
                >
                  <font-awesome icon="trash-alt" />
                  <span class="sr-only">Delete {{ item.name }}</span>
                </b-btn>
              </div>
            </td>
            <b-td v-if="isEditing(item)" colspan="4">
              <EditCategory
                :after-cancel="afterCancel"
                :after-save="afterSave"
                :existing-category="item"
                :position="position"
              />
            </b-td>
          </b-tr>
          <b-tr v-if="student">
            <b-td class="pl-0" colspan="4">
              <AddCourseToCategory
                :parent-category="category"
                :position="position"
                :student="student"
              />
            </b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
    </div>
    <AreYouSureModal
      v-if="courseForDelete"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :modal-body="`Are you sure you want to delete <strong>&quot;${courseForDelete.name}&quot;</strong>`"
      :show-modal="!!courseForDelete"
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
    category: {
      required: true,
      type: Object
    },
    items: {
      required: true,
      type: Array
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
    courseForDelete: undefined,
    courseForEdit: undefined,
    isAddingCourse: false
  }),
  computed: {
    hasFulfillments() {
      return !!this.student && !!this.$_.find(this.items, item => {
        return this.inspect(item, 'categoryId')
      })
    }
  },
  methods: {
    afterCancel() {
      this.$announcer.polite('Cancelled')
      this.putFocusNextTick(`column-${this.position}-edit-category-${this.courseForEdit.id}-btn`)
      this.courseForEdit = null
      this.setDisableButtons(false)
    },
    afterSave() {
      this.$announcer.polite(`Updated course ${this.courseForEdit.name}`)
      this.putFocusNextTick(`column-${this.position}-edit-category-${this.courseForEdit.id}-btn`)
      this.courseForEdit = null
      this.setDisableButtons(false)
    },
    deleteCanceled() {
      this.putFocusNextTick(`column-${this.position}-delete-course-${this.courseForDelete.id}-btn`)
      this.courseForDelete = null
      this.$announcer.polite('Canceled. Nothing deleted.')
      this.setDisableButtons(false)
    },
    deleteConfirmed() {
      this.deleteCategory(this.courseForDelete.id).then(() => {
        this.$announcer.polite(`${this.courseForDelete.name} deleted.`)
        this.courseForDelete = null
        this.setDisableButtons(false)
        this.putFocusNextTick('page-header')
      })
    },
    deleteCourse(item) {
      this.setDisableButtons(true)
      this.courseForDelete = item
      this.$announcer.polite(`Delete ${item.name}`)
    },
    edit(item) {
      this.setDisableButtons(true)
      this.$announcer.polite(`Edit ${item.name}`)
      this.courseForEdit = item
      this.putFocusNextTick(`column-${this.position}-name-input`)
    },
    inspect(item, key) {
      // TODO: What if multiple category has multiple fulfillments?
      return this.$_.size(item.fulfilledBy) ? item.fulfilledBy[0][key] : item[key]
    },
    isCourseRequirement: object => object.categoryType === 'Course Requirement',
    isEditing(item) {
      return item.id === this.$_.get(this.courseForEdit, 'id')
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