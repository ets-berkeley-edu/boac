<template>
  <div id="app" class="fill-viewport">
    <router-view></router-view>
  </div>
</template>

<script>
import router from '@/router';
import store from '@/store';
import Util from '@/mixins/Util';
import Vue from 'vue';
import VueAnalytics from 'vue-analytics';

export default {
  name: 'App',
  mixins: [Util],
  mounted() {
    this.asyncInit();
  },
  methods: {
    async asyncInit() {
      store.dispatch('context/loadConfig').then(response => {
        let googleAnalyticsId = this.get(response, 'googleAnalyticsId');
        if (googleAnalyticsId) {
          Vue.use(VueAnalytics, {
            id: googleAnalyticsId,
            debug: {
              // If debug.enabled is true then browser console gets GA debug info.
              enabled: false
            },
            router,
            checkDuplicatedScript: true
          });
        }
      });
      store.dispatch('user/loadUser').then(user => {
        if (user.isAuthenticated) {
          store.dispatch('cohort/loadMyCohorts');
          store.dispatch('curated/loadMyCuratedGroups');
          store.dispatch('context/loadServiceAnnouncement');
        }
      });
    }
  }
};
</script>

<style>
@import './assets/styles/bootstrap-overrides.css';
@import './assets/styles/boac-global.css';
</style>
