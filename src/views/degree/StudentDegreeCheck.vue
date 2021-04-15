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
        <h2 class="page-section-header">Create {{ student.firstName }}'s Degree Check</h2>
        <b-container class="px-0 mx-0" :fluid="true">
          <b-row>
            <b-col
              v-for="position in [1, 2, 3]"
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
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import TemplateCategoryColumn from '@/components/degree/TemplateCategoryColumn'
import Util from '@/mixins/Util'
import {getStudentByUid} from '@/api/student'
import {getDegreeChecks} from '@/api/degree'

export default {
  name: 'StudentDegreeCheck',
  mixins: [Context, Loading, Util],
  components: {
    DebugTemplate,
    Spinner,
    StudentProfileHeader,
    TemplateCategoryColumn
  },
  data: () => ({
    degree: undefined,
    student: undefined
  }),
  created() {
    const uid = this.$_.get(this.$route, 'params.uid')
    getStudentByUid(uid).then(data => {
      this.student = data
      this.setPageTitle(this.$currentUser.inDemoMode ? 'Student' : this.student.name)
      getDegreeChecks(data.sid).then(data => {
        this.degree = data
        this.loaded(`Degree Check for ${this.student.name}`)
      })
    })
  },
  methods: {
  }
}
</script>

<style>
.degree-check-column {
  min-width: 300px;
  padding-bottom: 10px;
}
</style>
