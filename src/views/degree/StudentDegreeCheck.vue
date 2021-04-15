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
        <b-container class="px-0 mx-0" :fluid="true">
          <b-row>
            <b-col>
              <h2 class="mb-1 page-section-header">Create {{ student.firstName }}'s Degree Check</h2>
              <div class="faint-text font-weight-500 font-size-18">
                Last updated {{ updatedAt | moment('MMM D, YYYY') }}
              </div>
            </b-col>
            <b-col>
              <div class="d-flex justify-content-end">
                <div class="pr-2">
                  <router-link
                    id="print-degree-plan"
                    :to="`/student/${student.uid}/degree/${templateId}/print`"
                  >
                    <font-awesome class="mr-1" icon="print" />
                    Print Plan
                  </router-link>
                </div>
                <div class="pr-2">
                  |
                </div>
                <div class="pr-2">
                  <router-link
                    id="view-degree-history"
                    :to="`/student/${student.uid}/degree/history`"
                  >
                    View Degree History
                  </router-link>
                </div>
                <div class="pr-2">
                  |
                </div>
                <div class="pr-2">
                  <router-link
                    id="create-new-degree"
                    :to="`/student/${student.uid}/degree/create`"
                  >
                    Create New Degree
                  </router-link>
                </div>
              </div>
            </b-col>
          </b-row>
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
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import TemplateCategoryColumn from '@/components/degree/TemplateCategoryColumn'
import Util from '@/mixins/Util'
import {getStudentByUid} from '@/api/student'

export default {
  name: 'StudentDegreeCheck',
  mixins: [Context, DegreeEditSession, Loading, Util],
  components: {
    DebugTemplate,
    Spinner,
    StudentProfileHeader,
    TemplateCategoryColumn
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
