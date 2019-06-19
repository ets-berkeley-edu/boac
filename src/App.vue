<template>
  <div id="app" class="fill-viewport">
    <router-view></router-view>
  </div>
</template>

<script>
import Context from '@/mixins/Context';

export default {
  name: 'App',
  mixins: [Context],
  mounted() {
    this.initUserSession().then(this.initGoogleAnalytics);
  }
};
</script>

<style>
@import './assets/styles/bootstrap-overrides.css';
@import './assets/styles/boac-global.css';
</style>
