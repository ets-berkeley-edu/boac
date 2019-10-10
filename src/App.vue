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
        <b>{{ getFixedWarningLabel() }}</b>
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
    getFixedWarningLabel() {
      let envName = undefined;
      if (this.includes(this.ebEnvironment, '_')) {
        envName = this.capitalize(this.split(this.ebEnvironment, '_')[1]);
      }
      return envName ? `BOA ${envName} Environment` : 'BOA Test Environment';
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
