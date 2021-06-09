<template>
  <div v-if="key">
    <div v-if="!courses[key].length" class="no-data-text">
      No courses
    </div>
    <div v-if="courses[key].length" :id="`${key}-courses-container`">
      <b-table-simple
        :id="`${key}-courses-table`"
        borderless
        class="mb-1 w-100 table-layout"
        responsive="md"
        small
      >
        <b-thead class="border-bottom">
          <b-tr class="sortable-table-header text-nowrap">
            <b-th v-if="$currentUser.canEditDegreeProgress" class="th-course-assignment-menu">
              <span class="sr-only">Options to assign course</span>
            </b-th>
            <b-th class="pl-0 th-name">Course</b-th>
            <b-th class="pl-0 text-right">Units</b-th>
            <b-th class="th-grade">Grade</b-th>
            <b-th v-if="!ignored" class="pl-0">Term</b-th>
            <b-th class="pl-0">Note</b-th>
            <b-th v-if="$currentUser.canEditDegreeProgress"></b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <template v-for="(course, index) in courses[key]">
            <b-tr
              :id="`${key}-course-${course.termId}-${course.sectionId}`"
              :key="`tr-${index}`"
              class="tr-course"
              :class="{'tr-while-dragging': isUserDragging(course.id)}"
              :draggable="!disableButtons && $currentUser.canEditDegreeProgress"
              @dragend="onDragEnd"
              @dragstart="onStartDraggingCourse(course)"
            >
              <td v-if="$currentUser.canEditDegreeProgress" class="td-course-assignment-menu">
                <div v-if="!isUserDragging(course.id)">
                  <CourseAssignmentMenu :course="course" />
                </div>
              </td>
              <td class="td-name">
                <span :class="{'font-weight-500': isEditing(course)}">{{ course.name }}</span>
              </td>
              <td class="td-units">
                <font-awesome
                  v-if="unitsWereEdited(course)"
                  :id="`${key}-course-units-were-edited-${course.termId}-${course.sectionId}`"
                  class="changed-units-icon"
                  icon="info-circle"
                  size="sm"
                  :title="`Updated from ${pluralize('unit', course.sis.units)}`"
                />
                <span class="font-size-14">{{ $_.isNil(course.units) ? '&mdash;' : course.units }}</span>
                <span v-if="unitsWereEdited(course)" class="sr-only"> (updated from {{ pluralize('unit', course.sis.units) }})</span>
              </td>
              <td class="td-grade">
                <span class="font-size-14">{{ course.grade || '&mdash;' }}</span>
              </td>
              <td v-if="!ignored" class="td-term">
                <span class="font-size-14">{{ course.termName }}</span>
              </td>
              <td class="td-note" :class="{'ellipsis-if-overflow': course.note}" :title="course.note || null">
                {{ course.note || '&mdash;' }}
              </td>
              <td v-if="$currentUser.canEditDegreeProgress" class="td-course-edit-button">
                <div v-if="!isUserDragging(course.id)">
                  <b-btn
                    :id="`edit-${key}-course-${course.id}-btn`"
                    class="font-size-14 p-0"
                    :disabled="disableButtons"
                    size="sm"
                    variant="link"
                    @click="edit(course)"
                  >
                    <font-awesome icon="edit" />
                    <span class="sr-only">Edit {{ course.name }}</span>
                  </b-btn>
                </div>
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
    ignored: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    courseForEdit: undefined,
    key: undefined
  }),
  created() {
    this.key = this.ignored ? 'ignored' : 'unassigned'
  },
  methods: {
    afterCancel() {
      this.$announcer.polite('Cancelled')
      this.$putFocusNextTick(`edit-${this.key}-course-${this.courseForEdit.id}-btn`)
      this.courseForEdit = null
      this.setDisableButtons(false)
    },
    afterSave(course) {
      this.courseForEdit = null
      this.$announcer.polite(`Updated ${this.key} course ${course.name}`)
      this.$putFocusNextTick(`edit-${this.key}-course-${course.termId}-${course.sectionId}-btn`)
      this.setDisableButtons(false)
    },
    edit(course) {
      this.setDisableButtons(true)
      this.$announcer.polite(`Edit ${this.key} ${course.name}`)
      this.courseForEdit = course
      this.$putFocusNextTick('name-input')
    },
    isEditing(course) {
      return course.sectionId === this.$_.get(this.courseForEdit, 'sectionId')
    },
    onStartDraggingCourse(course) {
      this.onDragStart({course, dragContext: this.key})
    }
  }
}
</script>

<style scoped>
table {
  border-collapse: separate;
  border-spacing: 0 0.05em;
}
.changed-units-icon {
  color: #00c13a;
  margin-right: 0.3em;
}
.ellipsis-if-overflow {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.table-layout {
  table-layout: fixed;
}
.td-course-assignment-menu {
  font-size: 14px;
  padding: 0 0.3em 0 0;
  vertical-align: middle;
  width: 14px;
}
.td-course-edit-button {
  padding-right: 0;
  vertical-align: middle;
  width: 32px;
}
.td-grade {
  padding: 0 0.5em 0 0.4em;
  vertical-align: middle;
  width: 30px;
}
.td-name {
  font-size: 14px;
  padding: 0.2em 0 0 0.25em;
  vertical-align: middle;
}
.td-note {
  max-width: 60px;
  padding: 0 0.5em 0 0;
  vertical-align: middle;
  width: 1px;
}
.td-term {
  vertical-align: middle;
  white-space: nowrap;
  width: 42px;
}
.td-units {
  text-align: right;
  padding: 0 0.5em 0 0;
  vertical-align: middle;
  white-space: nowrap;
  width: 50px;
}
.th-course-assignment-menu {
  padding: 0 0.3em 0 0;
  width: 14px;
}
.th-grade {
  width: 60px;
}
.th-name {
  max-width: 40%;
  width: 30%;
}
.tr-course {
  height: 36px;
}
.tr-while-dragging td:first-child, th:first-child {
  border-radius: 10px 0 0 10px;
}
.tr-while-dragging td:last-child, th:last-child {
  border-radius: 0 10px 10px 0;
}
</style>
