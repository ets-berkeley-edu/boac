<template>
  <div>
    <Spinner />
    <div v-if="!loading">
      <div class="border-bottom light-blue-background pb-2">
        <StudentProfileHeader
          :compact="true"
          :link-to-student-profile="true"
          :student="student"
        />
      </div>
      <div class="m-3 pt-2">
        <div class="section-separator w-100">
          <StudentDegreeCheckHeader
            :student="student"
            :degree-id="templateId"
            :degree-name="degreeName"
            :updated-at="updatedAt"
          />
        </div>
        <div class="d-flex section-separator w-100">
          <div class="w-50">
            <UnitRequirements template-id="templateId" />
          </div>
          <div>
            Unassigned Courses
          </div>
        </div>
        <b-container class="px-0 mx-0" :fluid="true">
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
import UnitRequirements from '@/components/degree/UnitRequirements'
import Util from '@/mixins/Util'
import {getStudentByUid} from '@/api/student'

export default {
  name: 'StudentDegreeCheck',
  mixins: [Context, DegreeEditSession, Loading, Util],
  components: {
    DebugTemplate,
    Spinner,
    StudentDegreeCheckHeader,
    StudentProfileHeader,
    TemplateCategoryColumn,
    UnitRequirements
  },
  data: () => ({
    student: undefined
  }),
  created() {
    const uid = this.$_.get(this.$route, 'params.uid')
    getStudentByUid(uid).then(data => {
      this.student = data
      const id = this.$_.get(this.$route, 'params.id')
      this.init(id).then(() => {
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
  border-bottom: 3px #999 solid;
  margin-bottom: 20px;
  padding-bottom: 10px;
}
</style>
