<template>
  <div id="student-profile-header">
    <div class="d-flex justify-content-between mr-4" :class="{'pb-0 pt-2': compact, 'pb-2 pt-4': !compact}">
      <div class="d-flex flex-row-reverse" :class="{'ml-3': compact, 'ml-5': !compact}">
        <div :class="{'mr-2 pr-2': compact, 'mr-4 pr-4': !compact}">
          <StudentProfileHeaderBio
            :compact="compact"
            :link-to-student-profile="linkToStudentProfile"
            :student="student"
          />
        </div>
        <div class="text-center" :class="{'column-with-avatar-compact': compact, 'column-with-avatar': !compact}">
          <StudentAvatar class="mb-2" :size="compact ? 'medium' : 'large'" :student="student" />
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
    this.$putFocusNextTick('student-name-header')
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
  margin: 0 64px 0 20px;
  vertical-align: center;
}
.column-with-avatar-compact {
  margin: 16px 32px 0 20px;
  vertical-align: center;
}
</style>
