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
        <div class="d-flex flex-wrap justify-content-between py-2 section-separator">
          <div class="pb-2 pr-2">
            <UnitRequirements :student="student" template-id="templateId" />
          </div>
          <div
            @drop="onDropToUnassignedCourses"
            @dragover.prevent
            @dragenter.prevent
          >
            <h2 class="font-size-20 font-weight-bold pb-0 text-nowrap">Unassigned Courses</h2>
            <UnassignedCourses :student="student" />
          </div>
        </div>
        <b-container class="mx-0 pt-3 px-0" :fluid="true">
          <b-row>
            <b-col
              v-for="position in [1, 2, 3]"
              :id="`student-degree-check-column-${position}`"
              :key="position"
              class="degree-check-column"
            >
              <TemplateCategoryColumn :position="position" :student="student" />
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
  methods: {
    onDropToUnassignedCourses() {
      this.onDrop({
        category: null,
        course: null,
        dropContext: 'unassigned',
        student: this.student
      })
    }
  }
}
</script>

<style>
.degree-check-column {
  min-width: 300px;
  padding-bottom: 10px;
}
.section-separator {
  border-bottom: 1px #999 solid;
}
</style>
