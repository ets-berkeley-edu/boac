<template>
  <v-fade-transition>
    <div class="d-flex flex-column min-viewport-height">
      <v-layout class="flex-grow-1">
        <v-app-bar
          color="primary"
          elevation="0"
          role="banner"
          tag="banner"
          @shortkey="() => putFocusNextTick('basic-search-input')"
        >
          <a id="skip-to-content-link" href="#content" class="sr-only sr-only-focusable align-self-start">Skip to main content</a>
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
                tabindex="-1"
              >
                <router-view :key="split(route.fullPath, '#', 1)[0]" />
              </div>
            </div>
          </div>
        </v-main>
      </v-layout>
      <footer class="flex-shrink-0" role="contentinfo">
        <AppFooter v-if="!loading && !hideFooter" />
      </footer>
    </div>
  </v-fade-transition>
</template>

<script setup lang="ts">
import {get, split} from 'lodash'
import {ref, useTemplateRef} from 'vue'
import {storeToRefs} from 'pinia'
import {useRoute} from 'vue-router'
import AppBar from '@/layouts/shared/AppBar.vue'
import AppFooter from '@/layouts/shared/AppFooter.vue'
import PlaneGoRound from '@/layouts/shared/PlaneGoRound.vue'
import ServiceAnnouncement from '@/layouts/shared/ServiceAnnouncement.vue'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const hideFooter = ref(false)
const route = useRoute()
const serviceAlert = useTemplateRef('serviceAlert')

const {loading} = storeToRefs(contextStore)
</script>

<style scoped>
.min-viewport-height {
  min-height: 100vh;
  /* dvh tracks mobile browser toolbars as they show and hide. Browsers without it use the 100vh above. */
  min-height: 100dvh;
}
</style>
