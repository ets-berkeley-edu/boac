<template>
  <div class="ml-3 mt-4 w-100">
    <h1 class="sr-only">Welcome to BOA</h1>

    <Spinner alert-prefix="Drop-in Advisor homepage" />

    <b-container v-if="!loading && showWaitlist" fluid>
      <b-row no-gutters>
        <b-col cols="7" sm>
          <div class="mb-4 mr-3">
            <button
              class="btn btn-link pl-0 pb-2"
              :disabled="onDuty"
              @click="hideDropInWaitlist()"
              @keyup.enter="hideDropInWaitlist()">
              Hide Drop-in Waitlist
            </button>
            <DropInWaitlist
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

    <b-container v-if="!loading && !showWaitlist" fluid>
      <button
        class="btn btn-link pl-0 pb-2"
        @click="showDropInWaitlist()"
        @keyup.enter="showDropInWaitlist()">
        Show Drop-in Waitlist
      </button>
      <div>
        <div id="filtered-cohorts-header-row">
          <h2 v-if="myCohorts && !size(myCohorts)" id="no-cohorts-header" class="page-section-header">
            You have no saved cohorts.
          </h2>
          <h1 v-if="myCohorts && size(myCohorts)" class="page-section-header">
            Cohorts
          </h1>
        </div>
        <div v-if="myCohorts && !size(myCohorts)">
          <router-link id="create-filtered-cohort" to="/cohort/new">Create a student cohort</router-link>
          automatically by your filtering preferences, such as GPA or units.
        </div>
        <div role="tablist" class="panel-group">
          <SortableGroup
            v-for="cohort in myCohorts"
            :key="cohort.id"
            :group="cohort"
            :is-cohort="true" />
        </div>
      </div>
      <div v-if="size(myCuratedGroups)">
        <div id="curated-groups-header-row">
          <h2 class="page-section-header">Curated Groups</h2>
        </div>
        <SortableGroup
          v-for="curatedGroup in myCuratedGroups"
          :key="curatedGroup.id"
          :group="curatedGroup"
          :is-cohort="false" />
      </div>
    </b-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import CurrentUserExtras from '@/mixins/CurrentUserExtras';
import DropInWaitlist from '@/components/appointment/DropInWaitlist';
import Loading from '@/mixins/Loading';
import Scrollable from '@/mixins/Scrollable';
import SortableGroup from '@/components/search/SortableGroup';
import Spinner from '@/components/util/Spinner';
import store from '@/store';
import Util from '@/mixins/Util';
import { getDropInAppointmentWaitlist } from '@/api/appointments';
import { setDropInStatus } from '@/api/user';

export default {
  name: 'DropInAdvisorHome',
  components: {
    DropInWaitlist,
    SortableGroup,
    Spinner
  },
  mixins: [Context, CurrentUserExtras, Loading, Scrollable, Util],
  data: () => ({
    deptCode: undefined,
    dropInStatus: undefined,
    loadingWaitlist: false,
    refreshJob: undefined,
    waitlist: undefined
  }),
  computed: {
    onDuty() {
      return this.dropInStatus && this.dropInStatus.startsWith('on_duty');
    },
    showWaitlist() {
      return this.dropInStatus !== 'off_duty_no_waitlist';
    }
  },
  created() {
    this.$eventHub.$on('drop-in-status-change', status => {
      this.dropInStatus = status;
    });
  },
  mounted() {
    this.deptCode = this.get(this.$route, 'params.deptCode').toUpperCase();
    this.layoutPage();
  },
  destroyed() {
    clearTimeout(this.refreshJob);
  },
  methods: {
    hideDropInWaitlist() {
      this.alertScreenReader('Hiding drop-in waitlist');
      this.loadingStart();
      setDropInStatus(this.deptCode, this.$currentUser.uid, 'off_duty_no_waitlist').then(() => {
        this.layoutPage();
      });
      clearTimeout(this.refreshJob);
    },
    layoutPage() {
      this.dropInStatus = this.get(this.find(this.$currentUser.dropInAdvisorStatus, {'deptCode': this.deptCode.toUpperCase()}), 'status');
      if (this.showWaitlist) {
        this.loadDropInWaitlist(true, true);
      } else {
        this.loaded('Home');
        this.scrollToTop();
      }
    },
    loadDropInWaitlist(scheduleFutureRefresh=true, announceLoad=false) {
      return new Promise(resolve => {
        if (this.loadingWaitlist) {
          resolve();
          if (this.showWaitlist && scheduleFutureRefresh) {
            this.scheduleRefreshJob();
          }
          return;
        }
        this.loadingWaitlist = true;
        getDropInAppointmentWaitlist(this.deptCode).then(response => {
          const waitlist = response.waitlist;
          let announceUpdate = false;

          if (!this.isEqual(waitlist, this.waitlist)) {
            if (this.waitlist) {
              announceUpdate = true;
            } else {
              announceLoad = true;
            }
            this.waitlist = waitlist;
          }

          const currentDropInStatus = this.find(this.$currentUser.dropInAdvisorStatus, {'deptCode': this.deptCode});
          const newDropInStatus = this.find(response.advisors, {'uid': this.$currentUser.uid});
          if (currentDropInStatus && newDropInStatus && currentDropInStatus.status !== newDropInStatus.status) {
            store.commit('currentUserExtras/setDropInStatus', {
              deptCode: this.deptCode,
              status: newDropInStatus.status
            });
          }

          this.loadingWaitlist = false;
          resolve();
          if (this.showWaitlist && scheduleFutureRefresh) {
            this.scheduleRefreshJob();
          }

          if (announceLoad) {
            this.loaded('Appointment waitlist');
          }
          if (announceUpdate) {
            this.alertScreenReader('The appointment waitlist has been updated');
          }
        });
      });
    },
    onAppointmentStatusChange() {
      // We return a Promise.
      return this.loadDropInWaitlist(false);
    },
    showDropInWaitlist() {
      this.alertScreenReader('Showing drop-in waitlist');
      this.loadingStart();
      setDropInStatus(this.deptCode, this.$currentUser.uid, 'off_duty_waitlist').then(() => {
        this.layoutPage();
      });
    },
    scheduleRefreshJob() {
      // Clear previous job, if pending. The following is null-safe.
      clearTimeout(this.refreshJob);
      this.refreshJob = setTimeout(this.loadDropInWaitlist, this.$config.apptDeskRefreshInterval);
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
