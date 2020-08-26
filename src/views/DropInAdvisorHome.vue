<template>
  <div class="ml-3 mt-4 w-100">
    <h1 class="sr-only">Welcome to BOA</h1>

    <Spinner alert-prefix="Drop-in Advisor homepage" />

    <b-container v-if="!loading" fluid>
      <b-row no-gutters>
        <b-col cols="7" sm>
          <div class="mb-4 mr-3">
            <DropInWaitlist
              :advisors="advisors"
              :dept-code="deptCode"
              :is-homepage="true"
              :on-appointment-status-change="onAppointmentStatusChange"
              :waitlist="waitlist" />
          </div>
        </b-col>
        <b-col cols="5" sm>
          <div class="homepage-alerts mr-3 pl-2">
            <div class="homepage-header-border">
              <h2 class="alerts-header mb-0 page-section-header">Alerts</h2>
            </div>
            <div v-if="myCohorts" class="mt-3">
              <div class="d-flex justify-content-between mr-3">
                <div>
                  <h3 class="color-grey font-size-14 font-weight-bold text-uppercase">Cohorts</h3>
                </div>
                <div v-if="myCohorts.length" class="color-grey font-size-14 font-weight-bold text-uppercase">
                  Total
                </div>
              </div>
              <div v-if="myCohorts.length">
                <SortableGroup
                  v-for="cohort in myCohorts"
                  :key="cohort.id"
                  :compact="true"
                  :group="cohort"
                  :is-cohort="true" />
              </div>
              <div v-if="!myCohorts.length">
                <div>
                  You have no saved cohorts.
                </div>
                <div>
                  <router-link id="create-filtered-cohort" to="/cohort/new">Create a student cohort</router-link>
                  automatically by your filtering preferences, such as GPA or units.
                </div>
              </div>
              <div v-if="size(myCuratedGroups)" class="mt-4">
                <div class="d-flex justify-content-between mr-3">
                  <div>
                    <h3 class="color-grey font-size-14 font-weight-bold text-uppercase">Curated Groups</h3>
                  </div>
                  <div v-if="myCuratedGroups.length" class="color-grey font-size-14 font-weight-bold text-uppercase">
                    Total
                  </div>
                </div>
                <SortableGroup
                  v-for="curatedGroup in myCuratedGroups"
                  :key="curatedGroup.id"
                  :group="curatedGroup"
                  :is-cohort="false"
                  :compact="true" />
              </div>
            </div>
          </div>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import DropInWaitlist from '@/components/appointment/DropInWaitlist'
import Loading from '@/mixins/Loading'
import SortableGroup from '@/components/search/SortableGroup'
import Spinner from '@/components/util/Spinner'
import store from '@/store'
import Util from '@/mixins/Util'
import { getDropInAppointmentWaitlist } from '@/api/appointments'

export default {
  name: 'DropInAdvisorHome',
  components: {
    DropInWaitlist,
    SortableGroup,
    Spinner
  },
  mixins: [Context, CurrentUserExtras, Loading, Util],
  data: () => ({
    advisors: undefined,
    deptCode: undefined,
    loadingWaitlist: false,
    refreshJob: undefined,
    waitlist: undefined
  }),
  mounted() {
    this.deptCode = this.get(this.$route, 'params.deptCode').toUpperCase()
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
          if (this.showWaitlist && scheduleFutureRefresh) {
            this.scheduleRefreshJob()
          }
          return
        }
        this.loadingWaitlist = true
        getDropInAppointmentWaitlist(this.deptCode).then(response => {
          const waitlist = response.waitlist
          let announceLoad = false
          let announceUpdate = false

          if (!this.isEqual(response.advisors, this.advisors)) {
            if (this.advisors) {
              announceUpdate = true
            }
            this.advisors = response.advisors
          }
          if (!this.isEqual(waitlist, this.waitlist)) {
            if (this.waitlist) {
              announceUpdate = true
            } else {
              announceLoad = true
            }
            this.waitlist = waitlist
          }

          const currentDropInStatus = this.find(this.$currentUser.dropInAdvisorStatus, {'deptCode': this.deptCode})
          const newDropInStatus = this.find(response.advisors, {'uid': this.$currentUser.uid})
          if (
            currentDropInStatus && newDropInStatus &&
            (currentDropInStatus.available !== newDropInStatus.available || currentDropInStatus.status !== newDropInStatus.status)
          ) {
            store.commit('currentUserExtras/setDropInStatus', {
              available: newDropInStatus.available,
              deptCode: this.deptCode,
              status: newDropInStatus.status,
            })
          }

          this.loadingWaitlist = false
          resolve()
          if (scheduleFutureRefresh) {
            this.scheduleRefreshJob()
          }

          if (announceLoad) {
            this.loaded('Appointment waitlist')
          }
          if (announceUpdate) {
            this.alertScreenReader('The appointment waitlist has been updated')
          }
        })
      })
    },
    onAppointmentStatusChange() {
      // We return a Promise.
      return this.loadDropInWaitlist(false)
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
.color-grey {
  color: #999;
}
</style>

<style>
.alerts-header {
  padding-top: 5px;
}
.homepage-alerts {
  max-width: 600px;
}
.homepage-header-border {
  border-bottom-color: lightgrey;
  border-bottom-style: solid;
  border-bottom-width: 4px;
  min-height: 50px;
}
</style>
