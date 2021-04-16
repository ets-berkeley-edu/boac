<template>
  <div>
    <div class="d-flex justify-content-between mr-4 pb-2 pt-4">
      <div class="d-flex flex-row-reverse mx-3">
        <div class="mr-2 pr-2">
          <StudentProfileHeaderBio
            :compact="compact"
            :link-to-student-profile="linkToStudentProfile"
            :student="student"
          />
        </div>
        <div class="column-with-avatar">
          <StudentAvatar :student="student" class="mb-2" size="large" />
          <ManageStudent v-if="!compact" :student="student" />
        </div>
      </div>
      <div class="mr-5">
        <StudentProfileHeaderAcademics :student="student" />
      </div>
    </div>
    <div v-if="!compact">
      <div class="d-flex justify-content-center pb-2">
        <div>
          <b-btn
            id="show-hide-personal-details"
            :aria-expanded="isShowingPersonalDetails"
            class="no-wrap"
            variant="link"
            @click="toggleShowDetails"
          >
            <font-awesome :icon="isShowingPersonalDetails ? 'caret-down' : 'caret-right'" :class="isShowingPersonalDetails ? 'mr-1' : 'ml-1 mr-1'" />
            {{ isShowingPersonalDetails ? 'Hide' : 'Show' }} Personal Details
          </b-btn>
        </div>
      </div>
      <div>
        <StudentPersonalDetails
          :inactive-majors="plansPartitionedByStatus[0].length ? plansPartitionedByStatus[1] : []"
          :inactive-minors="plansPartitionedByStatus[0].length ? plansMinorPartitionedByStatus[1] : []"
          :is-open="isShowingPersonalDetails"
          :student="student"
        />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import StudentAvatar from '@/components/student/StudentAvatar'
import StudentPersonalDetails from '@/components/student/profile/StudentPersonalDetails'
import StudentProfileHeaderAcademics from '@/components/student/profile/StudentProfileHeaderAcademics'
import StudentProfileHeaderBio from '@/components/student/profile/StudentProfileHeaderBio'
import Util from '@/mixins/Util'

export default {
  name: 'StudentProfileHeader',
  components: {
    ManageStudent,
    StudentAvatar,
    StudentPersonalDetails,
    StudentProfileHeaderAcademics,
    StudentProfileHeaderBio
  },
  mixins: [Context, Util],
  props: {
    compact: {
      required: false,
      type: Boolean
    },
    linkToStudentProfile: {
      required: false,
      type: Boolean
    },
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    isShowingPersonalDetails: false,
    plansMinorPartitionedByStatus: undefined,
    plansPartitionedByStatus: undefined
  }),
  created() {
    this.plansMinorPartitionedByStatus = this.$_.partition(this.student.sisProfile.plansMinor, (p) => p.status === 'Active')
    this.plansPartitionedByStatus = this.$_.partition(this.student.sisProfile.plans, (p) => p.status === 'Active')
  },
  mounted() {
    this.putFocusNextTick('student-name-header')
  },
  methods: {
    toggleShowDetails() {
      this.isShowingPersonalDetails = !this.isShowingPersonalDetails
      this.alertScreenReader(`Student details are ${this.isShowingPersonalDetails ? 'showing' : 'hidden'}.`)
    }
  }
}
</script>

<style>
.column-with-avatar {
  margin: 0 32px 0 20px;
  text-align: center;
  vertical-align: center;
}
</style>
