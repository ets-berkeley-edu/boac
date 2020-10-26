<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner />
    <div v-if="!loading && !$currentUser.isAdmin" class="mb-2 pb-3 pt-3 text-center">
      <b-btn
        id="btn-create-appointment"
        variant="primary"
        class="btn-primary-color-override mr-2 pl-3 pr-3"
        aria-label="Create appointment. Modal window will open."
        @click="openCreateAppointmentModal">
        New Drop-in Appointment
      </b-btn>
      <b-btn
        id="btn-log-resolved-isse"
        variant="outline-primary"
        class="btn-primary-color-override btn-primary-color-outline-override ml-2 pl-3 pr-3"
        aria-label="Log resolved issue. Modal window will open."
        @click="openLogResolvedIssueModal">
        Log Resolved Issue
      </b-btn>
    </div>
    <div v-if="!loading" class="drop-in-desk-outer pt-3">
      <div class="waitlist-container">
        <DropInAdvisorList
          :dept-code="deptCode"
          :advisors="advisors"
          :waitlist="waitlist" />
      </div>
      <div class="waitlist-container">
        <DropInWaitlist
          ref="dropInWaitlist"
          :advisors="advisors"
          :dept-code="deptCode"
          :on-appointment-status-change="onAppointmentStatusChange"
          :waitlist="waitlist" />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DropInAdvisorList from '@/components/appointment/DropInAdvisorList'
import DropInWaitlist from '@/components/appointment/DropInWaitlist'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import { getDropInAppointmentWaitlist } from '@/api/appointments'

export default {
  name: 'DropInDesk',
  components: {DropInAdvisorList, DropInWaitlist, Spinner},
  mixins: [Context, Loading, Util],
  data: () => ({
    advisors: undefined,
    loadingWaitlist: false,
    refreshJob: undefined,
    waitlist: undefined
  }),
  created() {
    this.deptCode = this.$_.get(this.$route, 'params.deptCode').toUpperCase()
    this.loadDropInWaitlist()
  },
  destroyed() {
    clearTimeout(this.refreshJob)
  },
  methods: {
    loadDropInWaitlist(scheduleFutureRefresh=true) {
      return new Promise(resolve => {
        if (this.loadingWaitlist) {
          resolve()
          if (scheduleFutureRefresh) {
            this.scheduleRefreshJob()
          }
          return
        }
        this.loadingWaitlist = true
        getDropInAppointmentWaitlist(this.deptCode).then(response => {
          let announceUpdate = false
          if (!this.$_.isEqual(response.advisors, this.advisors)) {
            if (this.advisors) {
              announceUpdate = true
            }
            this.advisors = response.advisors
          }
          if (!this.$_.isEqual(response.waitlist, this.waitlist)) {
            if (this.waitlist) {
              announceUpdate = true
            }
            this.waitlist = response.waitlist
          }

          this.loadingWaitlist = false
          resolve()
          if (scheduleFutureRefresh) {
            this.scheduleRefreshJob()
          }
          if (announceUpdate) {
            this.alertScreenReader('The drop-in wait-list has been updated')
          } else if (response.waitlist) {
            this.loaded('The Appointment wait-list has loaded')
          }
        })
      })
    },
    onAppointmentStatusChange() {
      // We return a Promise.
      return this.loadDropInWaitlist(false)
    },
    openCreateAppointmentModal() {
      if (this.$refs.dropInWaitlist) {
        this.$refs.dropInWaitlist.openCreateAppointmentModal()
      }
    },
    openLogResolvedIssueModal() {
      if (this.$refs.dropInWaitlist) {
        this.$refs.dropInWaitlist.openLogResolvedIssueModal()
      }
    },
    scheduleRefreshJob() {
      // Clear previous job, if pending. The following is null-safe.
      clearTimeout(this.refreshJob)
      this.refreshJob = setTimeout(this.loadDropInWaitlist, this.$config.apptDeskRefreshInterval)
    }
  }
}
</script>

<style scoped>
.drop-in-desk-outer {
  display: flex;
}
.waitlist-container {
  margin: 0 auto;
  width: 480px;
}
</style>
