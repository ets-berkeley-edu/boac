<template>
  <div id="app" class="fill-viewport">
    <router-view></router-view>
    <div v-if="fixedWarningOnAllPages && !hasUserDismissedFooterAlert" id="fixed_bottom">
      <div
        id="fixed-warning-on-all-pages"
        class="d-flex fixed-bottom fixed-warning"
        aria-expanded="true"
        aria-live="polite"
        role="alert">
        <div class="flex-grow-1">
          <b>BOA {{ getBoaEnvLabel() }} Environment</b>
        </div>
        <div>
          {{ fixedWarningOnAllPages }}
        </div>
        <div class="btn-wrapper ml-0 align-top">
          <b-btn
            class="btn-dismiss pl-2 pt-0 text-white"
            variant="link"
            aria-label="Dismiss warning about BOA environment type"
            @click="dismissFooterAlert">
            <font-awesome icon="plane-departure" />
          </b-btn>
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
.btn-dismiss {
  font-size: 14px;
}
.btn-wrapper {
  line-height: inherit;
  max-height: 16px;
  vertical-align: top;
}
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
