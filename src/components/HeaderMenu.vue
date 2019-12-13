<template>
  <div>
    <div v-if="!user"><font-awesome icon="spinner" spin class="b-link-text mr-4" /></div>
    <div v-if="user">
      <b-dropdown
        id="header-dropdown-under-name"
        class="mr-3"
        variant="link"
        no-caret
        right>
        <template slot="button-content">
          <div class="d-flex align-items-center">
            <div class="b-link-text">{{ user.firstName || `UID:${user.uid}` }}</div><font-awesome icon="caret-down" class="ml-1 b-link-text" />
          </div>
        </template>
        <b-dropdown-item v-if="user.isAdmin || $config.isDemoModeAvailable">
          <NavLink
            id="header-link-to-settings"
            class="nav-link-color text-decoration-none"
            :path="isUserSimplyScheduler() ? '/scheduler/settings' : '/admin'">
            <span v-if="user.isAdmin">Flight Deck</span>
            <span v-if="!user.isAdmin">Settings</span>
          </NavLink>
        </b-dropdown-item>
        <b-dropdown-item v-if="user.isAdmin">
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
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import NavLink from "@/components/util/NavLink";
import UserMetadata from '@/mixins/UserMetadata';
import { getCasLogoutUrl } from '@/api/auth';

export default {
  name: 'HeaderMenu',
  components: {NavLink},
  mixins: [Context, UserMetadata],
  methods: {
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
