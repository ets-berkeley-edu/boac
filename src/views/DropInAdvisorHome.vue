<template>
  <div class="ml-3 mt-3">
    <h1 class="sr-only">Welcome to BOA</h1>

    <Spinner alert-prefix="Drop-in Advisor homepage" />

    <b-container v-if="!loading" fluid>
      <b-row no-gutters>
        <b-col sm>
          <div class="mb-4 mr-4">
            <DropInWaitlist
              :dept-code="deptCode"
              :is-homepage="true"
              :on-appointment-cancellation="onAppointmentCancellation"
              :waitlist="waitlist" />
          </div>
        </b-col>
        <b-col sm>
          <div class="homepage-alerts mr-3">
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
import Context from '@/mixins/Context';
import DropInWaitlist from '@/components/appointment/DropInWaitlist';
import DropInWaitlistContainer from '@/mixins/DropInWaitlistContainer';
import Loading from '@/mixins/Loading';
import SortableGroup from '@/components/search/SortableGroup';
import Spinner from '@/components/util/Spinner';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'DropInAdvisorHome',
  components: {
    DropInWaitlist,
    SortableGroup,
    Spinner
  },
  mixins: [Context, DropInWaitlistContainer, Loading, UserMetadata, Util],
  data: () => ({
    deptCode: undefined,
    includeResolvedAppointments: true,
    waitlist: undefined
  }),
  mounted() {
    this.deptCode = this.get(this.$route, 'params.deptCode');
    this.loadDropInWaitlist();
    setInterval(this.loadDropInWaitlist, this.apptDeskRefreshInterval);
  },
  methods: {
    onAppointmentCancellation() {
      this.waitlist = this.partitionByCanceledStatus(this.waitlist);
    },
    partitionByCanceledStatus(waitlist) {
      const partitioned = this.partition(waitlist, a => !a.canceledAt);
      return partitioned[0].concat(partitioned[1]);
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
  max-height: 50px;
  min-height: 50px;
}
</style>
