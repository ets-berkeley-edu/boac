<template>
  <div id="app" class="fill-viewport">
    <VueAnnouncer />
    <router-view></router-view>
    <div v-if="$config.fixedWarningOnAllPages && !hasUserDismissedFooterAlert" id="fixed_bottom">
      <div id="fixed-warning-on-all-pages" class="d-flex fixed-bottom fixed-warning">
        <div class="flex-grow-1">
          <b>BOA {{ getBoaEnvLabel() }} Environment</b>
        </div>
        <div v-if="$config.isVueAppDebugMode">
          {{ $_.get($announcer.data, 'content') }}
        </div>
        <div v-if="!$config.isVueAppDebugMode">
          <span aria-live="polite" role="alert">{{ $config.fixedWarningOnAllPages }}</span>
        </div>
        <div class="btn-wrapper ml-0 align-top">
          <b-btn
            id="speedbird"
            class="btn-dismiss pl-2 pt-0 text-white"
            variant="link"
            aria-label="Dismiss warning about BOA environment type"
            @click="dismissTheWarning">
            <font-awesome icon="plane-departure" />
          </b-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'App',
  mixins: [Context],
  methods: {
    dismissTheWarning() {
      this.dismissFooterAlert()
      this.alertScreenReader('Warning message dismissed')
    },
    getBoaEnvLabel() {
      return this.$config.ebEnvironment ? this.$config.ebEnvironment.replace('boac-', '').toUpperCase() : 'Test'
    }
  }
}
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
