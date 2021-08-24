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
              :id="course.manuallyCreatedBy ? `${key}-course-${course.id}-manually-created` : `${key}-course-${course.termId}-${course.sectionId}`"
              :key="`tr-${index}`"
              class="tr-course"
              :class="{
                'accent-color-blue': course.accentColor === 'Blue',
                'accent-color-green': course.accentColor === 'Green',
                'accent-color-orange': course.accentColor === 'Orange',
                'accent-color-purple': course.accentColor === 'Purple',
                'accent-color-red': course.accentColor === 'Red',
                'cursor-grab': canDrag() && !draggingContext.course,
                'mouseover-grabbable': hoverCourseId === course.id && !draggingContext.course,
                'tr-while-dragging': isUserDragging(course.id)
              }"
              :draggable="canDrag()"
              @dragend="onDrag($event, 'end', course)"
              @dragenter="onDrag($event, 'enter', course)"
              @dragleave="onDrag($event, 'leave', course)"
              @dragover="onDrag($event, 'over', course)"
              @dragstart="onDrag($event, 'start', course)"
              @mouseenter="onMouse('enter', course)"
              @mouseleave="onMouse('leave', course)"
            >
              <td v-if="$currentUser.canEditDegreeProgress" class="td-course-assignment-menu">
                <div v-if="!isUserDragging(course.id)">
                  <CourseAssignmentMenu :after-course-assignment="() => $putFocusNextTick(`${key}-header`)" :course="course" />
                </div>
              </td>
              <td class="td-name">
                <span :class="{'font-weight-500': isEditing(course)}">{{ course.name }}</span>
              </td>
              <td class="td-units">
                <font-awesome
                  v-if="course.unitRequirements.length"
                  class="fulfillments-icon mr-1"
                  icon="check-circle"
                  size="sm"
                  :title="`Counts towards ${oxfordJoin($_.map(course.unitRequirements, 'name'))}`"
                />
                <font-awesome
                  v-if="unitsWereEdited(course)"
                  :id="course.manuallyCreatedBy ? `${key}-course-${course.id}-manually-created-units-edited` : `${key}-course-${course.termId}-${course.sectionId}-units-edited`"
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
                <span
                  :id="`course-${course.id}-note`"
                  v-linkified
                  v-html="course.note || '&mdash;'"
                />
              </td>
              <td v-if="$currentUser.canEditDegreeProgress" class="td-course-edit-button">
                <div class="d-flex">
                  <div v-if="course.manuallyCreatedBy" class="btn-container">
                    <b-btn
                      v-if="!isUserDragging(course.id)"
                      :id="`delete-${course.id}-btn`"
                      class="pl-0 pr-1 py-0"
                      :disabled="disableButtons"
                      size="sm"
                      variant="link"
                      @click="onDelete(course)"
                    >
                      <font-awesome icon="trash-alt" />
                      <span class="sr-only">Delete {{ course.name }}</span>
                    </b-btn>
                  </div>
                  <div class="btn-container">
                    <b-btn
                      v-if="!isUserDragging(course.id)"
                      :id="`edit-${key}-course-${course.id}-btn`"
                      class="font-size-14 pl-0 pr-1 py-0"
                      :disabled="disableButtons"
                      size="sm"
                      variant="link"
                      @click="edit(course)"
                    >
                      <font-awesome icon="edit" />
                      <span class="sr-only">Edit {{ course.name }}</span>
                    </b-btn>
                  </div>
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
    <AreYouSureModal
      v-if="courseForDelete"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :modal-body="`Are you sure you want to delete <strong>&quot;${courseForDelete.name}&quot;</strong>?`"
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
import EditCourse from '@/components/degree/student/EditCourse'
import Util from '@/mixins/Util'

export default {
  name: 'UnassignedCourses',
  mixins: [DegreeEditSession, Util],
  components: {AreYouSureModal, CourseAssignmentMenu, EditCourse},
  props: {
    ignored: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    courseForDelete: undefined,
    courseForEdit: undefined,
    hoverCourseId: undefined,
    key: undefined
  }),
  created() {
    this.key = this.ignored ? 'ignored' : 'unassigned'
  },
  methods: {
    afterCancel() {
      const putFocus = `edit-${this.key}-course-${this.courseForEdit.id}-btn`
      this.$announcer.polite('Cancelled')
      this.courseForEdit = null
      this.setDisableButtons(false)
      this.$putFocusNextTick(putFocus)
    },
    afterSave(course) {
      this.courseForEdit = null
      this.$announcer.polite(`Updated ${this.key} course ${course.name}`)
      this.setDisableButtons(false)
      this.$putFocusNextTick(`edit-${this.key}-course-${course.id}-btn`)
    },
    edit(course) {
      this.setDisableButtons(true)
      this.$announcer.polite(`Edit ${this.key} ${course.name}`)
      this.courseForEdit = course
      this.$putFocusNextTick('name-input')
    },
    canDrag() {
      return !this.disableButtons && this.$currentUser.canEditDegreeProgress
    },
    deleteCanceled() {
      this.$putFocusNextTick(`delete-${this.courseForDelete.id}-btn`)
      this.courseForDelete = null
      this.$announcer.polite('Canceled. Nothing deleted.')
      this.setDisableButtons(false)
    },
    deleteConfirmed() {
      return this.deleteCourse(this.courseForDelete.id).then(() => {
        this.$announcer.polite(`${this.courseForDelete.name} deleted.`)
        this.courseForDelete = null
        this.setDisableButtons(false)
        this.$putFocusNextTick('create-course-button')
      })
    },
    isEditing(course) {
      return course.sectionId === this.$_.get(this.courseForEdit, 'sectionId')
    },
    onDelete(course) {
      this.setDisableButtons(true)
      this.courseForDelete = course
      this.$announcer.polite(`Delete ${course.name}`)
    },
    onDrag(event, stage, course) {
      switch (stage) {
      case 'end':
        this.onDragEnd()
        break
      case 'start':
        if (event.target) {
          // Required for Safari
          event.target.style.opacity = 0.9
        }
        this.onDragStart({course, dragContext: this.key})
        break
      case 'enter':
      case 'exit':
      case 'leave':
      case 'over':
      default:
        break
      }
    },
    onMouse(stage, course) {
      switch(stage) {
      case 'enter':
        if (this.canDrag() && !this.draggingContext.course) {
          this.hoverCourseId = course.id
        }
        break
      case 'leave':
        this.hoverCourseId = null
        break
      default:
        break
      }
    }
  }
}
</script>

<style scoped>
table {
  border-collapse: separate;
  border-spacing: 0 0.05em;
}
.btn-container {
  min-width: 20px;
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
.fulfillments-icon {
  color: #00c13a;
}
.mouseover-grabbable td {
  background-color: #b9dcf0;
}
.mouseover-grabbable td:first-child {
  border-radius: 10px 0 0 10px;
}
.mouseover-grabbable td:last-child {
  border-radius: 0 10px 10px 0;
}
.table-layout {
  table-layout: fixed;
}
.td-course-assignment-menu {
  font-size: 14px;
  padding: 0 0 0 10px;
  vertical-align: middle;
  width: 14px;
}
.td-course-edit-button {
  padding-right: 0;
  vertical-align: middle;
  width: 24px;
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
.tr-while-dragging td {
  background-color: #125074;
  color: white;
}
.tr-while-dragging td:first-child {
  border-radius: 10px 0 0 10px;
}
.tr-while-dragging td:last-child {
  border-radius: 0 10px 10px 0;
}
</style>
