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
      <b-dropdown-item v-if="$currentUser.isAdmin || $config.isDemoModeAvailable">
        <NavLink
          id="header-link-to-settings"
          class="nav-link-color text-decoration-none"
          :path="isUserSimplyScheduler() ? '/scheduler/settings' : '/admin'">
          <span v-if="$currentUser.isAdmin">Flight Deck</span>
          <span v-if="!$currentUser.isAdmin">Settings</span>
        </NavLink>
      </b-dropdown-item>
      <b-dropdown-item v-if="$currentUser.isAdmin">
        <NavLink
          id="header-link-to-passengers"
          class="nav-link-color text-decoration-none"
          path="/admin/passengers">
          Passenger Manifest
        </NavLink>
      </b-dropdown-item>
      <b-dropdown-item href="#" @click="logOut">Log Out</b-dropdown-item>
      <b-dropdown-item
        :href="`mailto:${supportEmailAddress}`"
        target="_blank"
        aria-label="Send email to the BOA team">
        Feedback/Help<span class="sr-only"> (new browser tab will open)</span>
      </b-dropdown-item>
    </b-dropdown>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley';
import Context from '@/mixins/Context';
import NavLink from "@/components/util/NavLink";
import Util from '@/mixins/Util';
import { getCasLogoutUrl } from '@/api/auth';

export default {
  name: 'HeaderMenu',
  components: { NavLink },
  mixins: [Berkeley, Context, Util],
  methods: {
    isUserSimplyScheduler() {
     const isScheduler = this.size(this.myDeptCodes(['isScheduler']));
     return isScheduler && !this.$currentUser.isAdmin && !this.size(this.myDeptCodes(['isAdvisor', 'isDirector']));
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
