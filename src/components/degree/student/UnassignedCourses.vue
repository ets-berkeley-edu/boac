<template>
  <div>
    <div v-if="$_.isEmpty(courses.unassigned)" class="no-data-text">
      No courses
    </div>
    <div v-if="!$_.isEmpty(courses.unassigned)" id="unassigned-courses-container">
      <b-table-simple
        id="unassigned-courses-table"
        borderless
        class="mb-1 w-100"
        small
        stacked="sm"
      >
        <b-thead class="border-bottom">
          <b-tr class="sortable-table-header text-nowrap">
            <b-th></b-th>
            <b-th class="pl-0">Course</b-th>
            <b-th class="text-right">Units</b-th>
            <b-th>Grade</b-th>
            <b-th>Term</b-th>
            <b-th>Note</b-th>
            <b-th v-if="$currentUser.canEditDegreeProgress"></b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <template v-for="(course, index) in courses.unassigned">
            <b-tr
              :id="`unassigned-course-${course.termId}-${course.sectionId}`"
              :key="`tr-${index}`"
              class="bg-white"
              :draggable="!disableButtons && $currentUser.canEditDegreeProgress"
              @dragstart="onStartDraggingCourse(course)"
            >
              <td v-if="$currentUser.canEditDegreeProgress" class="font-size-14 td-course-assignment-menu">
                <CourseAssignmentMenu :course="course" :student="student" />
              </td>
              <td class="font-size-14 pl-0">
                <span :class="{'font-weight-500': isEditing(course)}">{{ course.name }}</span>
              </td>
              <td class="font-size-14 text-right">
                {{ $_.isNil(course.units) ? '&mdash;' : course.units }}
              </td>
              <td class="font-size-14">
                {{ course.grade || '&mdash;' }}
              </td>
              <td class="font-size-14">
                {{ course.termName }}
              </td>
              <td class="font-size-14">
                {{ course.note || '&mdash;' }}
              </td>
              <td v-if="$currentUser.canEditDegreeProgress" class="pr-0">
                <b-btn
                  :id="`edit-course-${course.id}-btn`"
                  class="font-size-14 px-0 pt-0"
                  :disabled="disableButtons"
                  size="sm"
                  variant="link"
                  @click="edit(course)"
                >
                  <font-awesome icon="edit" />
                  <span class="sr-only">Edit {{ course.name }}</span>
                </b-btn>
              </td>
            </b-tr>
            <b-tr v-if="isEditing(course)" :key="`tr-${index}-edit`">
              <b-td colspan="7">
                <EditCourse
                  :after-cancel="afterCancel"
                  :after-save="afterSave"
                  :course="course"
                  :position="0"
                />
              </b-td>
            </b-tr>
          </template>
        </b-tbody>
      </b-table-simple>
    </div>
  </div>
</template>

<script>
import CourseAssignmentMenu from '@/components/degree/student/CourseAssignmentMenu'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import EditCourse from '@/components/degree/student/EditCourse'
import Util from '@/mixins/Util'

export default {
  name: 'UnassignedCourses',
  mixins: [DegreeEditSession, Util],
  components: {CourseAssignmentMenu, EditCourse},
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
      this.courseForEdit = null
      this.$announcer.polite(`Updated course ${course.name}`)
      this.putFocusNextTick(`edit-course-${course.termId}-${course.sectionId}-btn`)
      this.setDisableButtons(false)
    },
    edit(course) {
      this.setDisableButtons(true)
      this.$announcer.polite(`Edit ${course.name}`)
      this.courseForEdit = course
      this.putFocusNextTick('name-input')
    },
    isEditing(course) {
      return course.sectionId === this.$_.get(this.courseForEdit, 'sectionId')
    },
    onStartDraggingCourse(course) {
      this.onDragStart({
        category: null,
        course: course,
        dragContext: 'unassigned',
        student: this.student,
      })
    }
  }
}
</script>

<style scoped>
.td-course-assignment-menu {
  padding-top: 2px;
}
</style>
