<template>
  <div id="app" class="fill-viewport">
    <router-view></router-view>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';

export default {
  name: 'App',
  mixins: [Context, Util],
  mounted() {
    this.initUserSession().then(this.noop);
  }
};
</script>

<style>
@import './assets/styles/bootstrap-overrides.css';
@import './assets/styles/boac-global.css';
</style>
