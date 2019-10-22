<template>
  <div class="ml-3 mt-3">
    <h1 class="sr-only">Welcome to BOA</h1>

    <Spinner alert-prefix="Drop-in Advisor homepage" />

    <div v-if="!loading">
      <div class="d-flex flex-wrap">
        <div class="flex-fill flex-grow-1 mb-4 mr-4">
          <DropInWaitlist :dept-code="deptCode" :is-homepage="true" :waitlist="waitlist" />
        </div>
        <div class="flex-fill homepage-alerts mr-3">
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
                <div v-if="myCohorts.length" class="color-grey font-size-14 font-weight-bold text-uppercase">
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
      </div>
    </div>
  </div>
</template>

<script>
import DropInWaitlist from "@/components/appointment/DropInWaitlist";
import Loading from '@/mixins/Loading';
import SortableGroup from '@/components/search/SortableGroup';
import Spinner from '@/components/util/Spinner';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { getDropInAppointmentWaitlist } from '@/api/appointments'

export default {
  name: 'DropInAdvisorHome',
  components: {
    DropInWaitlist,
    SortableGroup,
    Spinner
  },
  mixins: [Loading, UserMetadata, Util],
  data: () => ({
    deptCode: undefined,
    waitlist: undefined
  }),
  mounted() {
    this.deptCode = this.get(this.$route, 'params.deptCode');
    getDropInAppointmentWaitlist(this.deptCode, true).then(waitlist => {
      this.waitlist = waitlist;
      this.loaded();
    });
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
