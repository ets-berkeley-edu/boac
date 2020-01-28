<template>
  <div>
    <b-dropdown
      id="header-dropdown-under-name"
      class="mr-3"
      variant="link"
      no-caret
      right>
      <template slot="button-content">
        <div class="d-flex align-items-center">
          <div class="b-link-text">{{ $currentUser.firstName || `UID:${$currentUser.uid}` }}</div><font-awesome icon="caret-down" class="ml-1 b-link-text" />
        </div>
      </template>
      <b-dropdown-item
        v-if="$currentUser.isAdmin || getMyDirectorDept()"
        id="header-link-to-analytics"
        :href="$currentUser.isAdmin ? '/analytics/qcadv' : `/analytics/${getMyDirectorDept().toLowerCase()}`"
        class="nav-link-color text-decoration-none">
        Flight Data Recorder
      </b-dropdown-item>
      <b-dropdown-item
        v-if="!isUserSimplyScheduler() || size($currentUser.dropInAdvisorStatus) || $config.isDemoModeAvailable"
        id="header-link-to-settings"
        :href="isUserSimplyScheduler() ? '/scheduler/settings' : '/admin'"
        class="nav-link-color text-decoration-none">
        <span v-if="$currentUser.isAdmin">Flight Deck</span>
        <span v-if="!$currentUser.isAdmin">Settings</span>
      </b-dropdown-item>
      <b-dropdown-item
        v-if="$currentUser.isAdmin"
        id="header-link-to-passengers"
        href="/admin/passengers"
        class="nav-link-color text-decoration-none">
        Passenger Manifest
      </b-dropdown-item>
      <b-dropdown-item
        :href="`mailto:${$config.supportEmailAddress}`"
        target="_blank"
        aria-label="Send email to the BOA team">
        Feedback/Help<span class="sr-only"> (new browser tab will open)</span>
      </b-dropdown-item>
      <b-dropdown-item href="#" @click="logOut">Log Out</b-dropdown-item>
    </b-dropdown>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley';
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';
import { getCasLogoutUrl } from '@/api/auth';

export default {
  name: 'HeaderMenu',
  mixins: [Berkeley, Context, Util],
  methods: {
    getMyDirectorDept() {
      const deptCodes = this.myDeptCodes(['director']);
      return deptCodes && deptCodes[0];
    },
    isUserSimplyScheduler() {
      const isScheduler = this.size(this.myDeptCodes(['scheduler']));
      return isScheduler && !this.$currentUser.isAdmin && !this.size(this.myDeptCodes(['advisor', 'director']));
    },
    logOut() {
      getCasLogoutUrl().then(data => window.location.href = data.casLogoutUrl);
    }
  }
};
</script>

<style scoped>
.b-link-text {
  color: #fff;
}
.nav-link-color {
  color: #212529;
}
</style>
