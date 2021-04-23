<template>
  <div>
    <div v-if="$_.isEmpty(unassignedCourses)" class="no-data-text">
      No courses
    </div>
    <div v-if="!$_.isEmpty(unassignedCourses)" id="unassigned-courses-container">
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
            <b-th></b-th>
            <b-th class="pl-0">Course</b-th>
            <b-th>Units</b-th>
            <b-th>Grade</b-th>
            <b-th>Term</b-th>
            <b-th>Note</b-th>
            <b-th v-if="$currentUser.canEditDegreeProgress"></b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="(course, index) in unassignedCourses" :key="index">
            <td v-if="!isEditing(course)">
              <CourseAssignmentMenu
                :course="course"
                dropdown-boundary="#unassigned-courses-container"
                :student="student"
              />
            </td>
            <td v-if="!isEditing(course)">
              {{ course.name }}
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
            <td v-if="$currentUser.canEditDegreeProgress && !isEditing(course)" class="pr-0">
              <b-btn
                :id="`edit-course-${course.id}-btn`"
                class="px-0 pt-0"
                :disabled="disableButtons"
                variant="link"
                @click="edit(course)"
              >
                <font-awesome icon="edit" />
                <span class="sr-only">Edit {{ course.name }}</span>
              </b-btn>
            </td>
            <b-td v-if="isEditing(course)" colspan="6">
              <div class="border border-1 my-4 py-2 px-3 rounded">
                <div class="font-weight-500">{{ course.name }}</div>
                <EditUnassignedCourse
                  :after-cancel="afterCancel"
                  :after-save="afterSave"
                  :course="course"
                />
              </div>
            </b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
    </div>
  </div>
</template>

<script>
import CourseAssignmentMenu from '@/components/degree/student/CourseAssignmentMenu'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import EditUnassignedCourse from '@/components/degree/student/EditUnassignedCourse'
import Util from '@/mixins/Util'

export default {
  name: 'UnassignedCourses',
  mixins: [DegreeEditSession, Util],
  components: {CourseAssignmentMenu, EditUnassignedCourse},
  props: {
    student: {
      default: undefined,
      required: false,
      type: Object
    }
  },
  data: () => ({
    courseForEdit: undefined
  }),
  methods: {
    afterCancel() {
      this.$announcer.polite('Cancelled')
      this.putFocusNextTick(`edit-course-${this.courseForEdit.id}-btn`)
      this.courseForEdit = null
      this.setDisableButtons(false)
    },
    afterSave(course) {
      Object.assign(this.courseForEdit, course)
      this.courseForEdit = null
      this.refreshUnassignedCourses().then(() => {
        this.$announcer.polite(`Updated course ${course.name}`)
        this.putFocusNextTick(`edit-course-${course.termId}-${course.sectionId}-btn`)
        this.setDisableButtons(false)
      })
    },
    edit(course) {
      this.setDisableButtons(true)
      this.$announcer.polite(`Edit ${course.name}`)
      this.courseForEdit = course
      this.putFocusNextTick('name-input')
    },
    isEditing(course) {
      return course.sectionId === this.$_.get(this.courseForEdit, 'sectionId')
    }
  }
}
</script>
