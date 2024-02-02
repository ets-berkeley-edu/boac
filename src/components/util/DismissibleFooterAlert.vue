<template>
  <transition name="drawer">
    <div v-if="config.fixedWarningOnAllPages && !dismissedFooterAlert && !draggingContext.dragContext && !_get($route.meta, 'printable')" id="fixed_bottom">
      <div id="fixed-warning-on-all-pages" class="d-flex fixed-bottom fixed-warning">
        <div class="flex-grow-1">
          <b>BOA {{ getBoaEnvLabel() }} Environment</b>
        </div>
        <div v-if="config.isVueAppDebugMode">
          {{ _get(screenReaderAlert, 'message') }}
        </div>
        <div v-if="!config.isVueAppDebugMode">
          <span aria-live="polite" role="alert">{{ config.fixedWarningOnAllPages }}</span>
        </div>
        <div class="btn-wrapper ml-0 align-top">
          <b-btn
            id="speedbird"
            class="btn-dismiss pl-2 pt-0 text-white"
            variant="link"
            @click="dismissTheWarning"
          >
            <font-awesome icon="plane-departure" />
            <span class="sr-only">Dismiss warning about BOA environment type</span>
          </b-btn>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'

export default {
  name: 'DismissibleFooterAlert',
  mixins: [Context, DegreeEditSession, Util],
  methods: {
    dismissTheWarning() {
      this.dismissFooterAlert()
      this.$announcer.polite('Warning message dismissed')
    },
    getBoaEnvLabel() {
      return this.config.ebEnvironment ? this.config.ebEnvironment.replace('boac-', '').toUpperCase() : 'Test'
    }
  }
}
</script>

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
