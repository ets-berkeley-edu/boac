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
          <v-app-bar-nav-icon
            v-if="!mdAndUp"
            id="app-bar-nav-icon"
            aria-controls="small-viewport-sidebar"
            :aria-expanded="showSidebar"
            :aria-label="showSidebar ? 'Collapse navigation menu' : 'Expand navigation menu'"
            @click.stop="onToggleShowSidebar"
          />
          <AppBar />
        </v-app-bar>
        <v-navigation-drawer
          v-if="mdAndUp"
          aria-labelledby="nav-header"
          class="bg-tertiary pt-1 sidebar"
          permanent
          role="navigation"
          :scrim="false"
          tag="nav"
        >
          <template #append>
            <SidebarFooter v-if="currentUser.canAccessAdvisingData" />
          </template>
          <Sidebar />
        </v-navigation-drawer>
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
            <v-expand-transition>
              <div v-if="!mdAndUp && showSidebar && !loading">
                <Sidebar
                  id="small-viewport-sidebar"
                  class="bg-tertiary"
                  role="navigation"
                />
              </div>
            </v-expand-transition>
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
          <EditBatchNoteModal
            v-model="noteStore.isCreateNoteModalOpen"
            initial-mode="createBatch"
            :on-close="() => {
              noteStore.setMode(null)
              noteStore.setIsCreateNoteModalOpen(false)
              putFocusNextTick('batch-note-button')
            }"
          />
        </v-main>
      </v-layout>
      <footer
        :class="`footer-${smAndDown ? 'sm' : (mdAndDown ? 'md' : (lgAndDown ? 'lg' : 'xl'))}`"
        role="footer"
      >
        <AppFooter v-if="!loading && !hideFooter" />
      </footer>
    </div>
  </v-fade-transition>
</template>

<script setup lang="ts">
import {get, split} from 'lodash'
import {onBeforeUnmount, onMounted, ref, useTemplateRef, watch} from 'vue'
import {storeToRefs} from 'pinia'
import {useDisplay} from 'vuetify'
import {useRoute} from 'vue-router'
import AppBar from '@/layouts/shared/AppBar.vue'
import AppFooter from '@/layouts/shared/AppFooter.vue'
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal.vue'
import PlaneGoRound from '@/layouts/shared/PlaneGoRound.vue'
import ServiceAnnouncement from '@/layouts/shared/ServiceAnnouncement.vue'
import Sidebar from '@/components/sidebar/Sidebar.vue'
import SidebarFooter from '@/components/sidebar/SidebarFooter.vue'
import {putFocusNextTick, scrollTo} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const contextStore = useContextStore()
const hideFooter = ref(false)
const noteStore = useNoteStore()
const route = useRoute()
const serviceAlert = useTemplateRef('serviceAlert')
const serviceAlertOffset = ref<string | number>(0)
const showSidebar = ref(true)
const {currentUser, loading} = storeToRefs(contextStore)
const {lgAndDown, mdAndDown, mdAndUp, smAndDown} = useDisplay()

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

const onToggleShowSidebar = () => {
  showSidebar.value = !showSidebar.value
  if (showSidebar.value) {
    scrollTo('main-container', 'start')
  }
}

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
