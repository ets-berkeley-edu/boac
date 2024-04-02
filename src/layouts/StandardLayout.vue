<template>
  <v-layout class="h-100" style="overflow: visible !important">
    <v-app-bar color="primary" role="banner">
      <StandardHeaderLayout />
    </v-app-bar>
    <Sidebar />
    <v-main role="main">
      <ServiceAnnouncement />
      <router-view :key="stripAnchorRef($route.fullPath)"></router-view>
    </v-main>
    <v-footer app>
      <v-container v-if="!loading" class="px-6 pt-10 pb-4" fluid>
        <v-row>
          <v-col cols="12" md="4">
            <img alt="UC Berkeley logo" src="@/assets/uc-berkeley-logo.svg" />
          </v-col>
          <v-spacer />
          <v-col
            class="d-flex justify-end font-size-14 pr-0"
            cols="12"
            md="7"
            lg="5"
          >
            <div>
              <div>
                Problem? Question? Suggestion?
                Email <a :href="`mailto:${config.supportEmailAddress}`" target="_blank">{{ config.supportEmailAddress }}<span class="sr-only"> (new browser tab will open)</span></a>
              </div>
              &copy; {{ new Date().getFullYear() }} The Regents of the University of California
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-footer>
  </v-layout>
</template>

<script>
import Context from '@/mixins/Context'
import ServiceAnnouncement from '@/layouts/shared/ServiceAnnouncement'
import Sidebar from '@/components/sidebar/Sidebar'
import StandardHeaderLayout from '@/layouts/shared/StandardHeaderLayout'
import Util from '@/mixins/Util'

export default {
  name: 'StandardLayout',
  components: {
    ServiceAnnouncement,
    Sidebar,
    StandardHeaderLayout
  },
  mixins: [Context, Util],
  created() {
    this.putFocusNextTick('home-header')
  }
}
</script>
