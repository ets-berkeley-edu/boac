<template>
  <v-fade-transition>
    <div class="d-flex flex-column vh-100">
      <a id="skip-to-content-link" href="#content" class="sr-only">Skip to main content</a>
      <a id="skip-to-nav-link" href="#nav-header" class="sr-only">Skip to navigation</a>
      <v-layout>
        <v-app-bar
          color="primary"
          elevation="0"
          role="banner"
          tag="banner"
          @shortkey="() => putFocusNextTick('basic-search-input')"
        >
          <AppBar />
        </v-app-bar>
        <v-main role="none" tag="div">
          <div id="main-container" class="h-100">
            <div v-if="loading" class="loading-container align-center d-flex justify-center">
              <div class="ma-auto" role="progressbar">
                <PlaneGoRound
                  id="spinner-when-loading"
                  aria-label="page loading"
                  role="progressbar"
                  tabindex="0"
                />
              </div>
            </div>
            <div
              class="w-100"
              :class="{'service-alert-offset': get(contextStore, 'announcement.isPublished') && !contextStore.dismissedServiceAnnouncement}"
            >
              <ServiceAnnouncement ref="serviceAlert" />
              <div
                v-show="!loading"
                id="content"
                class="scroll-margins"
                role="main"
              >
                <router-view :key="split(route.fullPath, '#', 1)[0]" />
              </div>
            </div>
          </div>
        </v-main>
      </v-layout>
      <footer
        :class="`footer-${$vuetify.display.smAndDown ? 'sm' : ($vuetify.display.mdAndDown ? 'md' : ($vuetify.display.lgAndDown ? 'lg' : 'xl'))}`"
        role="footer"
      >
        <AppFooter v-if="!loading && !hideFooter" />
      </footer>
    </div>
  </v-fade-transition>
</template>

<script setup>
import AppBar from '@/layouts/shared/AppBar'
import AppFooter from '@/layouts/shared/AppFooter'
import PlaneGoRound from '@/layouts/shared/PlaneGoRound.vue'
import ServiceAnnouncement from '@/layouts/shared/ServiceAnnouncement'
import {get, split} from 'lodash'
import {onBeforeUnmount, onMounted, ref, useTemplateRef, watch} from 'vue'
import {putFocusNextTick} from '@/lib/utils'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()
const {loading} = storeToRefs(contextStore)

const hideFooter = ref(false)
const route = useRoute()
const serviceAlert = useTemplateRef('serviceAlert')
const serviceAlertOffset = ref(0)

watch(loading, value => {
  if (!value) {
    setServiceAlertOffset()
  }
})

onMounted(() => {
  contextStore.setEventHandler('hide-footer', setHideFooter)
})

onBeforeUnmount(() => {
  contextStore.removeEventHandler('hide-footer', setHideFooter)
})

const setHideFooter = value => hideFooter.value = value

const setServiceAlertOffset = () => {
  let counter = 0
  const setOffset = setInterval(() => {
    const height = get(serviceAlert.value, 'ref.clientHeight')
    if (height) {
      serviceAlertOffset.value = `${height}px`
    }
    if (height || ++counter > 2) {
      clearInterval(setOffset)
    }
  }, 500)
}
</script>

<style scoped>
.footer-sm {
  width: 97%;
}
.footer-md {
  margin-left: 256px;
  width: 74%;
}
.footer-lg {
  margin-left: 256px;
  width: 80%;
}
.footer-xl {
  margin-left: 256px;
  width: 83%;
}
.loading-container {
  height: calc(100vh - 64px);
}
</style>

<style>
.service-alert-offset > .scroll-margins,
.service-alert-offset h1.scroll-margins {
  scroll-margin-top: calc(v-bind(serviceAlertOffset) + 80px);
}
.sidebar .v-navigation-drawer__content {
  padding-bottom: 120px;
  scrollbar-width: none;
}
</style>
