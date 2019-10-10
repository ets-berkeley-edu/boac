<template>
  <div id="app" class="fill-viewport">
    <router-view></router-view>
    <div v-if="fixedWarningOnAllPages" id="fixed_bottom">
      <div
        id="fixed-warning-on-all-pages"
        class="fixed-bottom fixed-warning"
        aria-expanded="true"
        aria-live="polite"
        role="alert">
        <b>BOA {{ getBoaEnvLabel() }} Environment</b>
        <i class="icon-warning"></i>
        <div style="float: right;">
          {{ fixedWarningOnAllPages }}
        </div>
      </div>
    </div>
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
  },
  methods: {
    getBoaEnvLabel() {
      return this.ebEnvironment ? this.ebEnvironment.replace('boac-', '').toUpperCase() : 'Test';
    }
  }
};
</script>

<style>
@import './assets/styles/bootstrap-overrides.css';
@import './assets/styles/boac-global.css';
</style>

<style scoped>
.fixed-warning {
  background-color: #3b7ea5;
  border-color: #000;
  border-style: solid;
  border-width: 2px 0 0;
  color: #fff;
  opacity: 0.8;
  padding: 15px;
}
</style>
