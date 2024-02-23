<template>
  <b-container class="h-100 p-0" fluid>
    <b-row class="header" no-gutters>
      <StandardHeaderLayout role="banner" />
    </b-row>
    <b-row class="row-content" no-gutters>
      <b-col class="sidebar" sm="2">
        <Sidebar />
      </b-col>
      <b-col
        id="content"
        class="body-text h-100 pb-2"
        role="main"
        sm="10"
      >
        <ServiceAnnouncement />
        <router-view :key="stripAnchorRef($route.fullPath)"></router-view>
      </b-col>
    </b-row>
    <b-row class="row-footer" no-gutters>
      <b-col class="sidebar z-index-sub-zero" sm="2"></b-col>
      <b-col sm="10" role="contentinfo">
        <b-container v-if="!loading" fluid class="mb-3 ml-3 mt-5 p-0 w-auto">
          <b-row class="w-100">
            <b-col sm="7" class="mb-3 mr-auto">
              <img alt="UC Berkeley logo" src="@/assets/uc-berkeley-logo.svg" />
            </b-col>
            <b-col sm="5" class="pr-0">
              <div>
                Problem? Question? Suggestion?
                Email <a :href="`mailto:${config.supportEmailAddress}`" target="_blank">{{ config.supportEmailAddress }}<span class="sr-only"> (new browser tab will open)</span></a>
              </div>
              &copy; {{ new Date().getFullYear() }} The Regents of the University of California
            </b-col>
          </b-row>
        </b-container>
      </b-col>
    </b-row>
  </b-container>
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
.z-index-sub-zero {
  z-index: -1;
}
</style>
