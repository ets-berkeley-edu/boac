<template>
  <transition name="drawer">
    <div v-if="showAlert" id="fixed_bottom">
      <div id="fixed-warning-on-all-pages" class="align-center bg-primary d-flex fixed-bottom fixed-warning">
        <div class="flex-grow-1">
          <b>BOA {{ getBoaEnvLabel() }} Environment</b>
        </div>
        <div v-if="config.isVueAppDebugMode" class="mr-4">
          {{ get(contextStore.screenReaderAlert, 'message') }}
        </div>
        <div v-if="!config.isVueAppDebugMode" class="mr-4">
          <span aria-live="polite" role="alert">{{ config.fixedWarningOnAllPages }}</span>
        </div>
        <div>
          <v-btn
            id="speedbird"
            aria-label="Dismiss warning about BOA environment type"
            color="primary"
            :icon="mdiAirplane"
            size="sm"
            @click="dismissTheWarning"
          />
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {computed} from 'vue'
import {get} from 'lodash'
import {mdiAirplane} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const config = contextStore.config

const showAlert = computed(() => config.fixedWarningOnAllPages && !contextStore.dismissedFooterAlert)

const dismissTheWarning = () => {
  contextStore.dismissFooterAlert()
  alertScreenReader('Warning message dismissed')
}

const getBoaEnvLabel = () => {
  return config.ebEnvironment ? config.ebEnvironment.replace('boac-', '').toUpperCase() : 'Test'
}
</script>

<style scoped>
.fixed-bottom {
  position: fixed;
  left: 0;
  bottom: 0;
  width: 100%;
  z-index: 1000;
}
.fixed-warning {
  border-color: rgb(var(--v-theme-quaternary));;
  border-style: solid;
  border-width: 2px 0 0;
  color: rgb(var(--v-theme-on-primary));
  opacity: 0.9;
  padding: 15px;
}
</style>
