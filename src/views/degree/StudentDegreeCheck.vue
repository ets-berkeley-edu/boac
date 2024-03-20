<template>
  <div :class="{'cursor-grabbing': draggingContext.course}" @drag="scrollTo">
    <Spinner />
    <div v-if="!loading">
      <div class="border-bottom light-blue-background py-2">
        <StudentProfileHeader
          :compact="true"
          :link-to-student-profile="true"
          :student="student"
        />
      </div>
      <div class="m-3">
        <StudentDegreeCheckHeader :student="student" />
        <b-container class="px-0 py-2" fluid>
          <b-row no-gutters>
            <b-col cols="4">
              <UnitRequirements />
            </b-col>
            <b-col :cols="courses['ignored'].length ? 4 : 3">
              <div
                id="drop-zone-ignored-courses"
                class="drop-zone"
                :class="isDroppable('ignored') ? 'drop-zone-on' : 'drop-zone-off'"
                @dragend="onDrag($event, 'end', 'ignored')"
                @dragenter="onDrag($event,'enter', 'ignored')"
                @dragleave="onDrag($event, 'leave', 'ignored')"
                @dragexit="onDrag($event,'exit', 'ignored')"
                @dragover="onDrag($event,'over', 'ignored')"
                @dragstart="onDrag($event,'start', 'ignored')"
                @drop="dropToUnassign($event, 'ignored')"
              >
                <h3 id="ignored-header" class="font-size-20 font-weight-bold pb-0 text-no-wrap" tabindex="-1">Other Coursework</h3>
                <UnassignedCourses :ignored="true" />
              </div>
            </b-col>
            <b-col>
              <div
                id="drop-zone-unassigned-courses"
                class="drop-zone"
                :class="isDroppable('unassigned') ? 'drop-zone-on' : 'drop-zone-off'"
                @dragend="onDrag($event, 'end', 'unassigned')"
                @dragenter="onDrag($event,'enter', 'unassigned')"
                @dragleave="onDrag($event, 'leave', 'unassigned')"
                @dragexit="onDrag($event,'exit', 'unassigned')"
                @dragover="onDrag($event,'over', 'unassigned')"
                @dragstart="onDrag($event,'start', 'unassigned')"
                @drop="dropToUnassign($event, 'unassigned')"
              >
                <h3 id="unassigned-header" class="font-size-20 font-weight-bold pb-0 text-no-wrap" tabindex="-1">Unassigned Courses</h3>
                <div v-if="currentUser.canEditDegreeProgress" class="pb-2">
                  <DuplicateExistingCourse />
                </div>
                <UnassignedCourses />
              </div>
            </b-col>
          </b-row>
        </b-container>
        <h3 class="sr-only">Categories</h3>
        <b-container class="mx-0 pt-3 px-0" :fluid="true">
          <b-row>
            <b-col
              v-for="position in [1, 2, 3]"
              :id="`student-degree-check-column-${position}`"
              :key="position"
              class="degree-check-column"
            >
              <TemplateCategoryColumn :position="position" />
            </b-col>
          </b-row>
        </b-container>
        <DebugTemplate v-if="config.isVueAppDebugMode" />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DebugTemplate from '@/components/degree/DebugTemplate'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import DuplicateExistingCourse from '@/components/degree/student/DuplicateExistingCourse'
import Spinner from '@/components/util/Spinner'
import StudentDegreeCheckHeader from '@/components/degree/student/StudentDegreeCheckHeader'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import TemplateCategoryColumn from '@/components/degree/TemplateCategoryColumn'
import UnassignedCourses from '@/components/degree/student/UnassignedCourses'
import UnitRequirements from '@/components/degree/UnitRequirements'
import Util from '@/mixins/Util'
import {getStudentBySid} from '@/api/student'
import {onDrop, refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'

export default {
  name: 'StudentDegreeCheck',
  components: {
    DuplicateExistingCourse,
    DebugTemplate,
    Spinner,
    StudentDegreeCheckHeader,
    StudentProfileHeader,
    TemplateCategoryColumn,
    UnassignedCourses,
    UnitRequirements
  },
  mixins: [Context, DegreeEditSession, Util],
  data: () => ({
    previousClientY: 0,
    scrollHeight: undefined,
    student: undefined
  }),
  created() {
    this.onResize()
    window.addEventListener('resize', this.onResize)
    window.addEventListener('scroll', this.onResize)

    const degreeId = this._get(this.$route, 'params.id')
    refreshDegreeTemplate(degreeId).then(() => {
      getStudentBySid(this.sid, true).then(data => {
        this.student = data
        const studentName = this.currentUser.inDemoMode ? 'Student' : this.student.name
        this.setPageTitle(`${studentName} - ${this.degreeName}`)
        this.loadingComplete()
        this.alertScreenReader(`${this.degreeName} for ${this.student.name}`)
      })
    })
  },
  destroyed() {
    window.removeEventListener('resize', this.onResize)
    window.removeEventListener('scroll', this.onResize)
  },
  methods: {
    dropToUnassign(event, context) {
      event.stopPropagation()
      event.preventDefault()
      onDrop(null, context)
      this.setDraggingTarget(null)
    },
    isDroppable(target) {
      const course = this.draggingContext.course
      let droppable = this.draggingContext.target === target && course
      if (droppable) {
        if (target === 'ignored') {
          droppable = !course.ignore
        } else {
          droppable = course.ignore || course.categoryId
        }
      }
      return droppable
    },
    onDrag(event, stage, context) {
      switch (stage) {
      case 'end':
        this.setDraggingTarget(null)
        this.draggingContextReset()
        break
      case 'enter':
      case 'over':
        event.stopPropagation()
        event.preventDefault()
        this.setDraggingTarget(context)
        break
      case 'leave':
        if (this._get(event.target, 'id') === `drop-zone-${context}-courses`) {
          this.setDraggingTarget(null)
        }
        break
      case 'exit':
      case 'start':
      default:
        break
      }
    },
    scrollTo(event) {
      // Firefox does not need the intervention below.
      if (this.draggingContext.course && navigator.userAgent.indexOf('Firefox') === -1) {
        const eventY = event.clientY
        // Distance to bottom of viewport
        const distanceToBottom = window.innerHeight - eventY
        const magicNumber = 100
        // The closer to viewport top, or bottom, the faster the scroll.
        if (eventY >= this.previousClientY && distanceToBottom < magicNumber) {
          window.scrollTo({behavior: 'smooth', top: this.scrollHeight + magicNumber - distanceToBottom})
        } else if (eventY <= this.previousClientY && eventY < magicNumber) {
          window.scrollTo({behavior: 'smooth', top: window.scrollY + eventY - magicNumber})
        }
        this.previousClientY = eventY
      }
    },
    onResize() {
      this.scrollHeight = window.scrollY
    }
  }
}
</script>

<style scoped>
.cursor-grabbing {
  cursor: grabbing !important;
}
.degree-check-column {
  min-width: 300px;
  padding-bottom: 10px;
}
.drop-zone {
  margin-bottom: 0.5em;
  padding: 0.5em;
}
.drop-zone-on {
  background-color: #ecf5fb;
  border: #8bbdda dashed 0.15em;
}
.drop-zone-off {
  border: transparent dashed 0.15em;
}
.section-separator {
  border-bottom: 1px #999 solid;
}
</style>
