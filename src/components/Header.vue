<template>
  <div class="header-container">
    <div class="header-text">
      <legacy-link id="header-href-home" uri="/home">Home</legacy-link>
    </div>
    <div>
      <div class="header-dropdown-text">
        <div>
          <b-dropdown id="header-dropdown-under-name"
                      right
                      variant="link">
            <template slot="button-content">
              {{ user.firstName }}
            </template>
            <b-dd-item v-if="user.isAdmin">
              <legacy-link data-uri="'/admin'">Admin</legacy-link>
            </b-dd-item>
            <b-dd-item>
              <a :href="`mailto:${config.supportEmailAddress}`" target="_blank">Feedback/Help</a>
            </b-dd-item>
          </b-dropdown>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getCasLogoutURL } from '@/api/user';
import LegacyLink from '@/components/links/legacy.vue';
import store from '@/store';

export default {
  name: 'Header',
  components: {
    LegacyLink
  },
  computed: {
    config() {
      return store.getters.config;
    },
    user() {
      return store.getters.user;
    }
  },
  methods: {
    logOut() {
      getCasLogoutURL().then(data => {
        window.location.href = data.casLogoutURL;
      });
    }
  }
};
</script>

<style scoped lang="scss">
.header-container {
  align-items: center;
  display: flex;
  height: 56px;
  justify-content: space-between;
}
.header-container div:last-child {
  flex-grow: 0;
}
.header-container div:last-child > span {
  float: right;
}
.header-container div:last-child > button {
  float: right;
  margin-right: 20px;
}
</style>
