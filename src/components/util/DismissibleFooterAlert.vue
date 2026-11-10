<template>
  <transition name="drawer">
    <div v-if="showAlert" id="fixed-bottom" role="complementary">
      <!-- The banner is fixed, so it takes no room in the page. This spacer matches its height so the end of the
           page (e.g. the footer) can scroll clear of it, even when larger text makes the banner taller. -->
      <div aria-hidden="true" :style="{height: `${bannerHeight}px`}" />
      <div
        id="fixed-warning-on-all-pages"
        ref="banner"
        class="align-center bg-primary d-flex fixed-bottom"
      >
        <div class="flex-grow-1">
          <b class="sr-only">BOA {{ getBoaEnvLabel() }} Environment</b>
        </div>
        <div v-if="config.isVueAppDebugMode" class="mr-4">
          {{ contextStore.screenReaderAlert.message }}
        </div>
        <div v-if="!config.isVueAppDebugMode" class="mr-4">
          <span aria-live="polite">{{ config.fixedWarningOnAllPages }}</span>
        </div>
        <div>
          <v-btn
            id="speedbird"
            aria-label="Dismiss BOA environment type warning"
            class="text-white"
            color="primary"
            :icon="mdiAirplane"
            size="sm"
            title="Dismiss"
            @click="dismissTheWarning"
          />
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import {computed, onBeforeUnmount, ref, watch} from 'vue'
import {mdiAirplane} from '@mdi/js'
import {alertScreenReader} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const config = contextStore.config

const showAlert = computed(() => config.fixedWarningOnAllPages && !contextStore.dismissedFooterAlert)
const banner = ref(null)
const bannerHeight = ref(0)
// Track the banner's rendered height, which changes with window width and the user's text size.
const resizeObserver = new ResizeObserver(entries => {
  bannerHeight.value = entries[0].target.offsetHeight
})

watch(banner, (element, previous) => {
  if (previous) {
    resizeObserver.unobserve(previous)
  }
  if (element) {
    resizeObserver.observe(element)
  }
})

onBeforeUnmount(() => resizeObserver.disconnect())

const dismissTheWarning = () => {
  contextStore.dismissFooterAlert()
  alertScreenReader('Warning dismissed')
}

const getBoaEnvLabel = () => {
  return config.ebEnvironment ? config.ebEnvironment.replace('boac-', '').toUpperCase() : 'Test'
}
</script>

<style scoped>
.fixed-bottom {
  border-color: rgb(var(--v-theme-quaternary));;
  border-style: solid;
  border-width: 2px 0 0;
  bottom: 0;
  left: 0;
  opacity: 0.9;
  padding: 15px 24px;
  position: fixed;
  width: 100%;
  z-index: 1000;
}
</style>
