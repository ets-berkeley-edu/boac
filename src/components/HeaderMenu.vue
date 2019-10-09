<template>
  <div>
    <div v-if="!user"><font-awesome icon="spinner" spin class="b-link-text mr-4" /></div>
    <div v-if="user">
      <span v-if="user && !user.firstName">{{ user }}</span>
      <b-dropdown
        id="header-dropdown-under-name"
        class="mr-3"
        variant="link"
        no-caret
        right>
        <template slot="button-content">
          <div class="d-flex align-items-center">
            <div class="b-link-text">{{ user.firstName }}</div><font-awesome icon="caret-down" class="ml-1 b-link-text" />
          </div>
        </template>
        <b-dropdown-item v-if="user.isAdmin || isDemoModeAvailable" @click="goAdmin">Admin</b-dropdown-item>
        <b-dropdown-item href="#" @click="logOut">Log Out</b-dropdown-item>
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
    logOut() {
      getCasLogoutUrl().then(data => window.location.href = data.casLogoutUrl);
    },
    goAdmin() {
      this.$router.push({ path: '/admin' });
    }
  }
};
</script>

<style scoped>
.b-link-text {
  color: #fff;
}
</style>
