<template>
  <div>
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
        <div class="section-separator w-100">
          <StudentDegreeCheckHeader :student="student" />
        </div>
        <b-container class="px-0 py-2 section-separator" fluid>
          <b-row no-gutters>
            <b-col class="pb-2 pr-2 pt-1">
              <UnitRequirements />
            </b-col>
            <b-col>
              <div
                id="drop-zone-unassigned-courses"
                class="drop-zone"
                :class="{
                  'drop-zone-on': draggingContext.target === 'unassigned',
                  'drop-zone-off': draggingContext.target !== 'unassigned'
                }"
                @dragend="onDrag($event, 'end')"
                @dragenter="onDrag($event,'enter')"
                @dragleave="onDrag($event, 'leave')"
                @dragexit="onDrag($event,'exit')"
                @dragover="onDrag($event,'over')"
                @drop="dropToUnassign"
              >
                <h2 class="font-size-20 font-weight-bold pb-0 text-nowrap">Unassigned Courses</h2>
                <UnassignedCourses />
              </div>
            </b-col>
          </b-row>
        </b-container>
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
        <div v-if="$config.isVueAppDebugMode" class="pt-5">
          <DebugTemplate />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DebugTemplate from '@/components/degree/DebugTemplate'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import StudentDegreeCheckHeader from '@/components/degree/student/StudentDegreeCheckHeader'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import TemplateCategoryColumn from '@/components/degree/TemplateCategoryColumn'
import UnassignedCourses from '@/components/degree/student/UnassignedCourses'
import UnitRequirements from '@/components/degree/UnitRequirements'
import Util from '@/mixins/Util'
import {getStudentBySid} from '@/api/student'

export default {
  name: 'StudentDegreeCheck',
  mixins: [Context, DegreeEditSession, Loading, Util],
  components: {
    DebugTemplate,
    Spinner,
    StudentDegreeCheckHeader,
    StudentProfileHeader,
    TemplateCategoryColumn,
    UnassignedCourses,
    UnitRequirements
  },
  data: () => ({
    student: undefined
  }),
  created() {
    window.addEventListener('drag', this.scrollPerDrag)
    const degreeId = this.$_.get(this.$route, 'params.id')
    this.init(degreeId).then(() => {
      getStudentBySid(this.sid, true).then(data => {
        this.student = data
        const studentName = this.$currentUser.inDemoMode ? 'Student' : this.student.name
        this.setPageTitle(`${studentName} - ${this.degreeName}`)
        this.loaded(`${this.degreeName} for ${this.student.name}`)
      })
    })
  },
  destroyed() {
    window.removeEventListener('drag', this.scrollPerDrag)
  },
  methods: {
    scrollPerDrag(event) {
      if (event && this.draggingContext.dragContext === 'unassigned' && !this.draggingContext.target) {
        window.scroll({
          top: event.y,
          left: event.x,
          behavior: 'smooth'
        })
      }
    },
    dropToUnassign(event) {
      event.stopPropagation()
      event.preventDefault()
      this.onDrop({category: null, context: 'unassigned'})
      this.setDraggingTarget(null)
    },
    onDrag(event, stage) {
      switch (stage) {
      case 'end':
        this.setDraggingTarget(null)
        this.onDragEnd()
        break
      case 'enter':
      case 'over':
        event.stopPropagation()
        event.preventDefault()
        if (this.draggingContext.dragContext !== 'unassigned') {
          this.setDraggingTarget('unassigned')
        }
        break
      case 'leave':
        if (this.$_.get(event.target, 'id') === 'drop-zone-unassigned-courses') {
          this.setDraggingTarget(null)
        }
        break
      case 'exit':
      default:
        break
      }
    }
  }
}
</script>

<style>
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
