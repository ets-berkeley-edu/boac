<template>
  <v-fade-transition>
    <v-app>
      <a id="skip-to-content-link" href="#content" class="sr-only">Skip to main content</a>
      <v-layout>
        <v-app-bar
          color="primary"
          elevation="0"
          @shortkey="() => putFocusNextTick('search-students-input')"
        >
          <AppBar />
        </v-app-bar>
        <v-navigation-drawer
          absolute
          class="bg-tertiary pt-1"
          :location="$vuetify.display.mdAndUp ? 'start' : 'top'"
          permanent
        >
          <Sidebar />
        </v-navigation-drawer>
        <v-main id="content">
          <div class="h-100" :class="{'align-center d-flex justify-center': loading}">
            <PlaneGoRound v-if="loading" />
            <div v-show="!loading" class="pa-4 w-100">
              <ServiceAnnouncement />
              <router-view :key="split($route.fullPath, '#', 1)[0]" />
            </div>
          </div>
        </v-main>
        <v-footer v-if="!loading" app color="transparent">
          <AppFooter />
        </v-footer>
      </v-layout>
    </v-app>
  </v-fade-transition>
</template>

<script setup>
import AppBar from '@/layouts/shared/AppBar'
import AppFooter from '@/layouts/shared/AppFooter'
import PlaneGoRound from '@/layouts/shared/PlaneGoRound.vue'
import ServiceAnnouncement from '@/layouts/shared/ServiceAnnouncement'
import Sidebar from '@/components/sidebar/Sidebar'
import {computed} from 'vue'
import {putFocusNextTick} from '@/lib/utils'
import {split} from 'lodash'
import {useContextStore} from '@/stores/context'

const loading = computed(() => useContextStore().loading)
putFocusNextTick('home-header')
</script>
