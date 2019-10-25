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
        <b-dropdown-item v-if="user.isAdmin || isDemoModeAvailable" @click="goFlightDeck">
          <span v-if="user.isAdmin">Flight Deck</span>
          <span v-if="!user.isAdmin">Settings</span>
        </b-dropdown-item>
        <b-dropdown-item v-if="user.isAdmin" @click="goPassengerManifest">
          Passenger Manifest
        </b-dropdown-item>
        <b-dropdown-item @click="logOut" href="#">Log Out</b-dropdown-item>
        <b-dropdown-item :href="`mailto:${supportEmailAddress}`" target="_blank">Feedback/Help</b-dropdown-item>
      </b-dropdown>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import { getCasLogoutUrl } from '@/api/auth';

export default {
  name: 'HeaderMenu',
  mixins: [Context, UserMetadata],
  methods: {
    goFlightDeck() {
      this.$router.push({ path: this.isUserSimplyScheduler() ? '/scheduler/settings' : '/admin' });
    },
    logOut() {
      getCasLogoutUrl().then(data => window.location.href = data.casLogoutUrl);
    },
    goPassengerManifest() {
      this.$router.push({ path: '/admin/passengers' });
    }
  }
};
</script>

<style scoped>
.b-link-text {
  color: #fff;
}
</style>
