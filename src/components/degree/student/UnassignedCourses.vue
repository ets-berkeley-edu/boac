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
      >
        <b-thead class="border-bottom">
          <b-tr class="sortable-table-header text-nowrap">
            <b-th class="td-course-assignment-menu"></b-th>
            <b-th class="pl-0 td-course-name">Course</b-th>
            <b-th class="text-right">Units</b-th>
            <b-th class="td-grade">Grade</b-th>
            <b-th class="td-term">Term</b-th>
            <b-th>Note</b-th>
            <b-th v-if="$currentUser.canEditDegreeProgress"></b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <template v-for="(course, index) in courses.unassigned">
            <b-tr
              :id="`unassigned-course-${course.termId}-${course.sectionId}`"
              :key="`tr-${index}`"
              :class="{'drag-and-drop-tr': isUserDragging(course.id)}"
              :draggable="!disableButtons && $currentUser.canEditDegreeProgress"
              @dragend="onDragEnd"
              @dragstart="onStartDraggingCourse(course)"
            >
              <td
                v-if="$currentUser.canEditDegreeProgress"
                class="align-middle font-size-14 td-course-assignment-menu"
              >
                <CourseAssignmentMenu :course="course" :student="student" />
              </td>
              <td class="align-middle ellipsis-if-overflow font-size-14 td-course-name text-nowrap">
                <span :class="{'font-weight-500': isEditing(course)}">{{ course.name }}</span>
              </td>
              <td class="align-middle font-size-14 text-right">
                {{ $_.isNil(course.units) ? '&mdash;' : course.units }}
              </td>
              <td class="align-middle font-size-14 td-grade">
                {{ course.grade || '&mdash;' }}
              </td>
              <td class="align-middle font-size-14 td-term text-nowrap">
                {{ course.termName }}
              </td>
              <td class="align-middle ellipsis-if-overflow font-size-14 td-note text-nowrap">
                {{ course.note || '&mdash;' }}
              </td>
              <td v-if="$currentUser.canEditDegreeProgress" class="align-middle pr-0 td-course-edit-button">
                <b-btn
                  v-if="!isUserDragging(course.id)"
                  :id="`edit-course-${course.id}-btn`"
                  class="font-size-14 p-0"
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
td:first-child,
th:first-child {
  border-radius: 10px 0 0 10px;
}
td:last-child,
th:last-child {
  border-radius: 0 10px 10px 0;
}

.ellipsis-if-overflow {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.td-course-assignment-menu {
  padding: 2px 0 2px 8px;
  width: 6px;
}
.td-course-edit-button {
  height: 36px;
  width: 32px;
}
.td-course-name {
  padding: 2px 0 0 6px;
  width: 1px;
}
.td-grade {
  width: 32px;
}
.td-note {
  max-width: 240px;
  width: 1px;
}
.td-term {
  width: 42px;
}
</style>
