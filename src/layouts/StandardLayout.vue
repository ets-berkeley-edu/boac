<template>
  <v-container class="h-100 pa-0" fluid>
    <v-row class="header" no-gutters>
      <StandardHeaderLayout role="banner" />
    </v-row>
    <v-row class="row-content" no-gutters>
      <v-col class="sidebar" sm="2">
        <Sidebar />
      </v-col>
      <v-col
        id="content"
        class="body-text h-100 pb-2"
        role="main"
        sm="10"
      >
        <ServiceAnnouncement />
        <router-view :key="stripAnchorRef($route.fullPath)"></router-view>
      </v-col>
    </v-row>
    <v-row class="row-footer" no-gutters>
      <v-col class="sidebar z-index-sub-zero" sm="2"></v-col>
      <v-col sm="10" role="contentinfo">
        <v-container v-if="!loading" fluid class="mb-3 ml-3 mt-5 pa-0 w-auto">
          <v-row class="w-100">
            <v-col sm="7" class="mb-3 mr-auto">
              <img alt="UC Berkeley logo" src="@/assets/uc-berkeley-logo.svg" />
            </v-col>
            <v-col sm="5" class="pr-0">
              <div>
                Problem? Question? Suggestion?
                Email <a :href="`mailto:${config.supportEmailAddress}`" target="_blank">{{ config.supportEmailAddress }}<span class="sr-only"> (new browser tab will open)</span></a>
              </div>
              &copy; {{ new Date().getFullYear() }} The Regents of the University of California
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>
  </v-container>
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

<style scoped>
.body-text {
  font-size: 16px;
}
.header {
  background-color: #3b7ea5;
}
.row-content {
  min-height: 82%;
}
.row-footer {
  min-height: 18%;
}
.sidebar {
  background-color: #125074;
}
.z-index-sub-zero {
  z-index: -1;
}
</style>
