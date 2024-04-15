<template>
  <v-app>
    <a id="skip-to-content-link" href="#content" class="sr-only">Skip to main content</a>
    <v-layout>
      <v-app-bar
        color="primary"
        elevation="0"
        @shortkey="() => putFocusNextTick('search-students-input')"
      >
        <div class="align-center d-flex flex-nowrap justify-space-between my-2 w-100">
          <div
            class="font-size-16 header-text ml-3 text-white"
            role="banner"
          >
            <span class="hide-in-narrow-viewport">
              <span v-if="startsWith($route.path, '/home')" class="text-no-wrap">
                <span class="font-weight-bold">UC Berkeley</span>
                Online Advising
              </span>
              <router-link
                v-if="!startsWith($route.path, '/home')"
                id="home-header"
                class="text-no-wrap"
                to="/"
              >
                <span class="font-weight-bold">UC Berkeley</span>
                Online Advising
              </router-link>
            </span>
            <router-link id="home-header" class="show-in-narrow-viewport" to="/">
              <v-icon :icon="mdiHome" color="white" />
            </router-link>
          </div>
          <div class="ml-3">
            <AdvancedSearch />
          </div>
          <div class="mx-3">
            <HeaderMenu />
          </div>
        </div>
      </v-app-bar>
      <v-navigation-drawer
        absolute
        class="bg-tertiary pt-1"
        :location="$vuetify.display.mdAndUp ? 'start' : 'top'"
        permanent
      >
        <Sidebar />
      </v-navigation-drawer>
      <v-main>
        <ServiceAnnouncement />
        <router-view :key="split($route.fullPath, '#', 1)[0]" />
      </v-main>
      <v-footer app color="transparent">
        <div v-if="!loading" class="d-flex flex-wrap justify-space-between px-3 pt-10 pb-4 w-100">
          <div>
            <img alt="UC Berkeley logo" src="@/assets/uc-berkeley-logo.svg" />
          </div>
          <div class="font-size-14 pr-0">
            <div>
              Problem? Question? Suggestion?
              Email <a :href="`mailto:${supportEmailAddress}`" target="_blank">{{ supportEmailAddress }}<span class="sr-only"> (new browser tab will open)</span></a>
            </div>
            <div>
              &copy; {{ new Date().getFullYear() }} The Regents of the University of California
            </div>
          </div>
        </div>
      </v-footer>
    </v-layout>
  </v-app>
</template>

<script setup>
import AdvancedSearch from '@/components/search/AdvancedSearch'
import HeaderMenu from '@/components/header/HeaderMenu'
import ServiceAnnouncement from '@/layouts/shared/ServiceAnnouncement'
import Sidebar from '@/components/sidebar/Sidebar'
import {computed} from 'vue'
import {mdiHome} from '@mdi/js'
import {putFocusNextTick} from '@/lib/utils'
import {split, startsWith} from 'lodash'
import {useContextStore} from '@/stores/context'

const loading = computed(() => useContextStore().loading)
const supportEmailAddress = useContextStore().config.supportEmailAddress
putFocusNextTick('home-header')
</script>

<style scoped>
.header-text a:link,
.header-text a:visited {
  color: #fff;
  text-decoration: none;
  border: 0;
  -moz-outline-style: none;
}
.header-text a:hover,
.header-text a:focus,
.header-text a:active {
  color: #ddd;
}
.header-text h1 {
  font-size: inherit;
  font-weight: inherit;
}
@media (max-width: 600px) {
  .hide-in-narrow-viewport {
    display: none;
  }
}
@media (min-width: 600px) {
  .show-in-narrow-viewport {
    display: none;
  }
}
</style>
