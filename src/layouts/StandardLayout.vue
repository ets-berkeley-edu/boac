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
        <Footer v-if="!loading" class="mb-3 ml-3 mt-5" />
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import Context from '@/mixins/Context'
import Footer from '@/components/Footer'
import Loading from '@/mixins/Loading'
import ServiceAnnouncement from '@/layouts/shared/ServiceAnnouncement'
import Sidebar from '@/components/sidebar/Sidebar'
import StandardHeaderLayout from '@/layouts/shared/StandardHeaderLayout'
import Util from '@/mixins/Util'

export default {
  name: 'StandardLayout',
  components: {
    Footer,
    ServiceAnnouncement,
    Sidebar,
    StandardHeaderLayout
  },
  mixins: [Context, Loading, Util],
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
