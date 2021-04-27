<template>
  <div>
    <div v-if="$_.isEmpty(courses)" class="no-data-text">
      No courses
    </div>
    <div
      v-if="!$_.isEmpty(courses)"
      :id="`column-${position}-course-table-${courses[0].parentCategoryId}`"
    >
      <b-table-simple
        :id="`column-${position}-courses-of-category-${courses[0].parentCategoryId}`"
        borderless
        small
      >
        <b-thead class="border-bottom">
          <b-tr class="sortable-table-header text-nowrap">
            <b-th v-if="hasFulfillments"></b-th>
            <b-th class="pl-0 table-cell-course">Course</b-th>
            <b-th class="table-cell-units">Units</b-th>
            <b-th>Fulfillment</b-th>
            <b-th v-if="$currentUser.canEditDegreeProgress" class="sr-only">Actions</b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="(course, index) in courses" :id="`course-${course.id}-table-row`" :key="index">
            <td v-if="student && hasFulfillments && !isEditing(course)" class="pt-0">
              <CourseAssignmentMenu
                v-if="inspect(course, 'categoryId')"
                :course="course.fulfilledBy[0]"
                :student="student"
              />
            </td>
            <td
              v-if="!isEditing(course)"
              class="font-size-14 pl-0 pr-3 table-cell-course"
            >
              {{ inspect(course, 'name') }}
            </td>
            <td
              v-if="!isEditing(course)"
              class="float-right font-size-14 pr-2 table-cell-units text-nowrap"
            >
              <span class="font-size-14">{{ inspect(course, 'units') || '&mdash;' }}</span>
            </td>
            <td
              v-if="!isEditing(course)"
              class="font-size-14 td-max-width-0"
              :title="oxfordJoin($_.map(course.unitRequirements, 'name'), 'None')"
            >
              <div class="align-items-start d-flex justify-content-between">
                <div class="ellipsis-if-overflow">
                  {{ oxfordJoin($_.map(course.unitRequirements, 'name'), '&mdash;') }}
                </div>
                <div v-if="$_.size(course.unitRequirements) > 1" class="unit-requirement-count">
                  <span class="sr-only">(Has </span>{{ course.unitRequirements.length }}<span class="sr-only"> requirements.)</span>
                </div>
              </div>
            </td>
            <td v-if="$currentUser.canEditDegreeProgress && !student && !isEditing(course)" class="pr-0 w-10">
              <div class="d-flex justify-content-end text-nowrap">
                <b-btn
                  :id="`column-${position}-edit-category-${course.id}-btn`"
                  class="pl-0 pr-2 pt-0"
                  :disabled="disableButtons"
                  size="sm"
                  variant="link"
                  @click="edit(course)"
                >
                  <font-awesome icon="edit" />
                  <span class="sr-only">Edit {{ course.name }}</span>
                </b-btn>
                <b-btn
                  :id="`column-${position}-delete-course-${course.id}-btn`"
                  class="px-0 pt-0"
                  :disabled="disableButtons"
                  size="sm"
                  variant="link"
                  @click="deleteCourse(course)"
                >
                  <font-awesome icon="trash-alt" />
                  <span class="sr-only">Delete {{ course.name }}</span>
                </b-btn>
              </div>
            </td>
            <b-td v-if="isEditing(course)" colspan="4">
              <EditCategory
                :after-cancel="afterCancel"
                :after-save="afterSave"
                :existing-category="course"
                :position="position"
              />
            </b-td>
          </b-tr>
          <b-tr v-if="student">
            <b-td class="pl-0" colspan="4">
              <b-btn
                v-if="$currentUser.canEditDegreeProgress"
                :id="`column-${position}-add-course-to-category-${courses[0].parentCategoryId}`"
                class="align-items-center d-flex flex-row-reverse p-0"
                :disabled="disableButtons"
                variant="link"
                @click.prevent="onClickAddCourse"
              >
                <div class="font-size-14 text-nowrap">
                  Add Course
                </div>
                <div class="font-size-14 pr-1">
                  <font-awesome icon="plus" />
                </div>
              </b-btn>
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
import AreYouSureModal from '@/components/util/AreYouSureModal'
import CourseAssignmentMenu from '@/components/degree/student/CourseAssignmentMenu'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import EditCategory from '@/components/degree/EditCategory'
import Util from '@/mixins/Util'

export default {
  name: 'CoursesTable',
  mixins: [DegreeEditSession, Util],
  components: {CourseAssignmentMenu, EditCategory, AreYouSureModal},
  props: {
    courses: {
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
    hasFulfillments: undefined
  }),
  created() {
    this.hasFulfillments = !!this.$_.find(this.courses, course => {
      return this.inspect(course, 'categoryId')
    })
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
    deleteCourse(course) {
      this.setDisableButtons(true)
      this.courseForDelete = course
      this.$announcer.polite(`Delete ${course.name}`)
    },
    edit(course) {
      this.setDisableButtons(true)
      this.$announcer.polite(`Edit ${course.name}`)
      this.courseForEdit = course
      this.putFocusNextTick(`column-${this.position}-name-input`)
    },
    inspect(course, key) {
      // TODO: What if multiple category has multiple fulfillments?
      return this.$_.size(course.fulfilledBy) ? course.fulfilledBy[0][key] : course[key]
    },
    isEditing(course) {
      return course.id === this.$_.get(this.courseForEdit, 'id')
    },
    onClickAddCourse() {
      this.$announcer.polite('onClickAddCourse')
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