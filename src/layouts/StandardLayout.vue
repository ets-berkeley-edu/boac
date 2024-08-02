<template>
  <v-fade-transition>
    <div class="vh-100">
      <a id="skip-to-content-link" href="#content" class="sr-only">Skip to main content</a>
      <v-layout class="h-100">
        <v-app-bar
          color="primary"
          elevation="0"
          @shortkey="() => putFocusNextTick('search-students-input')"
        >
          <v-app-bar-nav-icon
            v-if="!$vuetify.display.mdAndUp"
            id="app-bar-nav-icon"
            aria-controls="small-viewport-sidebar"
            :aria-label="showSidebar ? 'Collapse navigation menu' : 'Expand navigation menu'"
            @click.stop="showSidebar = !showSidebar"
          />
          <AppBar />
        </v-app-bar>
        <v-navigation-drawer
          v-if="$vuetify.display.mdAndUp"
          class="bg-tertiary pt-1 sidebar"
          permanent
          :scrim="false"
        >
          <template #append>
            <SidebarFooter v-if="currentUser.canAccessAdvisingData" />
          </template>
          <Sidebar />
        </v-navigation-drawer>
        <v-main id="content">
          <div class="h-100" :class="{'align-center d-flex justify-center': loading}">
            <PlaneGoRound v-if="loading" />
            <v-expand-transition>
              <Sidebar
                v-if="!$vuetify.display.mdAndUp && showSidebar && !loading"
                id="small-viewport-sidebar"
                class="bg-tertiary"
              />
            </v-expand-transition>
            <div v-show="!loading" class="w-100">
              <ServiceAnnouncement />
              <router-view :key="split($route.fullPath, '#', 1)[0]" />
            </div>
          </div>
          <v-footer
            v-if="!loading"
            absolute
            class="align-end w-100"
            color="transparent"
            location="bottom"
          >
            <AppFooter />
          </v-footer>
        </v-main>
      </v-layout>
    </div>
  </v-fade-transition>
</template>

<script setup>
import AppBar from '@/layouts/shared/AppBar'
import AppFooter from '@/layouts/shared/AppFooter'
import SidebarFooter from '@/components/sidebar/SidebarFooter.vue'
import PlaneGoRound from '@/layouts/shared/PlaneGoRound.vue'
import ServiceAnnouncement from '@/layouts/shared/ServiceAnnouncement'
import Sidebar from '@/components/sidebar/Sidebar'
import {putFocusNextTick} from '@/lib/utils'
import {ref} from 'vue'
import {split} from 'lodash'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'

const currentUser = useContextStore().currentUser
const {loading} = storeToRefs(useContextStore())
const showSidebar = ref(true)

putFocusNextTick('home-header')
</script>

<style>
.sidebar .v-navigation-drawer__content {
  padding-bottom: 120px;
  scrollbar-width: none;
}
</style>
