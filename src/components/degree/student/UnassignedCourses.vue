<template>
  <div>
    <div v-if="$_.isEmpty(courses)" class="no-data-text">
      No courses
    </div>
    <div v-if="!$_.isEmpty(courses)">
      <b-table-simple
        id="unassigned-courses-table"
        borderless
        class="w-100"
        :responsive="true"
        small
        stacked="sm"
      >
        <b-thead class="border-bottom">
          <b-tr class="sortable-table-header text-nowrap">
            <b-th class="pl-0">Course</b-th>
            <b-th>Units</b-th>
            <b-th>Grade</b-th>
            <b-th>Term</b-th>
            <b-th>Note</b-th>
            <b-th></b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="course in courses" :key="course.id">
            <td v-if="!isEditing(course)">
              {{ course.displayName }}
            </td>
            <td v-if="!isEditing(course)">
              <span class="font-size-14">{{ $_.isNil(course.units) ? '&mdash;' : course.units }}</span>
            </td>
            <td v-if="!isEditing(course)">
              {{ course.grade || '&mdash;' }}
            </td>
            <td v-if="!isEditing(course)">
              {{ course.termName }}
            </td>
            <td v-if="!isEditing(course)">
              {{ course.note }}
            </td>
            <td v-if="!isEditing(course)" class="pr-0">
              <b-btn
                :id="`edit-course-${course.id}-btn`"
                class="degree-progress-edit-delete-btn"
                :disabled="disableButtons"
                variant="link"
                @click="edit(course)"
              >
                <font-awesome icon="edit" />
                <span class="sr-only">Edit {{ course.name }}</span>
              </b-btn>
            </td>
            <b-td v-if="isEditing(course)" colspan="4">
              <EditUnassignedCourse
                :after-cancel="afterCancel"
                :after-save="afterSave"
                :existing-course="course"
              />
            </b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
    </div>
  </div>
</template>

<script>
import DegreeEditSession from '@/mixins/DegreeEditSession'
import EditUnassignedCourse from '@/components/degree/student/EditUnassignedCourse'
import Util from '@/mixins/Util'
import {getUnassignedCourses} from '@/api/degree'

export default {
  name: 'UnassignedCourses',
  mixins: [DegreeEditSession, Util],
  components: {EditUnassignedCourse},
  props: {
    student: {
      default: undefined,
      required: false,
      type: Object
    }
  },
  data: () => ({
    courses: undefined,
    courseForEdit: undefined
  }),
  created() {
    getUnassignedCourses(this.templateId).then(data => {
      this.courses = data
    })
  },
  methods: {
    afterCancel() {
      this.$announcer.polite('Cancelled')
      this.putFocusNextTick(`edit-course-${this.courseForEdit.id}-btn`)
      this.courseForEdit = null
      this.setDisableButtons(false)
    },
    afterSave() {
      this.$announcer.polite(`Updated course ${this.courseForEdit.name}`)
      this.putFocusNextTick(`edit-course-${this.courseForEdit.id}-btn`)
      this.courseForEdit = null
      this.setDisableButtons(false)
    },
    edit(course) {
      this.setDisableButtons(true)
      this.$announcer.polite(`Edit ${course.name}`)
      this.courseForEdit = course
      this.putFocusNextTick('name-input')
    },
    isEditing(course) {
      return false && course.id === this.$_.get(this.courseForEdit, 'id')
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