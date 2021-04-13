<template>
  <div>
    <div v-if="$_.isEmpty(courses)" class="no-data-text">
      No courses
    </div>
    <b-table-simple
      id="unit-requirements-table"
      borderless
      :responsive="true"
      small
      stacked="sm"
    >
      <b-thead class="border-bottom">
        <b-tr class="sortable-table-header text-nowrap">
          <b-th>Course</b-th>
          <b-th>Units</b-th>
          <b-th>Fulfillment</b-th>
          <b-th></b-th>
        </b-tr>
      </b-thead>
      <b-tbody>
        <b-tr v-for="course in courses" :key="course.id">
          <td v-if="!isEditing(course)" class="td-truncate-with-ellipsis" :title="course.name">{{ course.name }}</td>
          <td v-if="!isEditing(course)">
            <span class="font-size-14">{{ $_.isNil(course.courseUnits) ? '&mdash;' : course.courseUnits }}</span>
          </td>
          <td v-if="!isEditing(course)" class="td-truncate-with-ellipsis" :title="oxfordJoin($_.map(course.unitRequirements, 'name'), 'None')">
            {{ oxfordJoin($_.map(course.unitRequirements, 'name'), '&mdash;') }}
          </td>
          <td v-if="!isEditing(course)">
            <div class="d-flex justify-content-end">
              <b-btn
                :id="`column-${position}-edit-category-${course.id}-btn`"
                class="font-size-14 pl-1 pr-0 py-0"
                :disabled="disableButtons"
                variant="link"
                @click="edit(course)"
              >
                <font-awesome icon="edit" />
                <span class="sr-only">Edit {{ course.name }}</span>
              </b-btn>
              <b-btn
                :id="`column-${position}-delete-course-${course.id}-btn`"
                class="font-size-14 pl-1 pr-0 py-0"
                :disabled="disableButtons"
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
      </b-tbody>
    </b-table-simple>
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
import DegreeEditSession from '@/mixins/DegreeEditSession'
import EditCategory from '@/components/degree/EditCategory'
import Util from '@/mixins/Util'

export default {
  name: 'CoursesTable',
  mixins: [DegreeEditSession, Util],
  components: {EditCategory, AreYouSureModal},
  props: {
    courses: {
      required: true,
      type: Array
    },
    position: {
      required: true,
      type: Number
    }
  },
  data: () => ({
    courseForDelete: undefined,
    courseForEdit: undefined
  }),
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
    isEditing(course) {
      return course.id === this.$_.get(this.courseForEdit, 'id')
    }
  }
}
</script>

<style scoped>
.td-truncate-with-ellipsis {
  max-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>