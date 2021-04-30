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
        <div class="d-flex py-3 section-separator w-100">
          <div class="pr-2 w-50">
            <UnitRequirements :student="student" template-id="templateId" />
          </div>
          <div class="pl-2 w-50">
            <h2 class="page-section-header-sub text-nowrap pb-2">Unassigned Courses</h2>
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
      getStudentBySid(this.sid).then(data => {
        this.student = data
        const studentName = this.$currentUser.inDemoMode ? 'Student' : this.student.name
        this.setPageTitle(`${studentName} - ${this.degreeName}`)
        this.loaded(`${this.degreeName} for ${this.student.name}`)
      })
    })
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
