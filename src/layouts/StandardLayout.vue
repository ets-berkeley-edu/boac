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
          v-if="$vuetify.display.mdAndUp"
          absolute
          class="bg-tertiary pt-1"
          location="start"
          permanent
        >
          <Sidebar />
        </v-navigation-drawer>
        <v-main id="content">
          <div class="h-100" :class="{'align-center d-flex justify-center': loading}">
            <PlaneGoRound v-if="loading" />
            <Sidebar v-if="!$vuetify.display.mdAndUp" class="bg-tertiary" />
            <div v-show="!loading" class="h-100 w-100">
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
import {putFocusNextTick} from '@/lib/utils'
import {split} from 'lodash'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'

const {loading} = storeToRefs(useContextStore())

putFocusNextTick('home-header')
</script>
