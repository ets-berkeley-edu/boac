<template>
  <b-container class="h-100 p-0" fluid>
    <StandardHeaderLayout />
    <b-row class="row-content" no-gutters>
      <b-col id="content" class="body-text h-100 min-width-100 pb-2" sm="10">
        <ServiceAnnouncement />
        <div>
          <router-view :key="stripAnchorRef($route.fullPath)"></router-view>
        </div>
      </b-col>
    </b-row>
    <b-row class="row-footer" no-gutters>
      <b-col class="min-width-100" sm="10">
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
import StandardHeaderLayout from '@/layouts/shared/StandardHeaderLayout'
import Util from '@/mixins/Util'

export default {
  name: 'AppointmentDropIn',
  components: {
    Footer,
    ServiceAnnouncement,
    StandardHeaderLayout
  },
  mixins: [Context, Loading, Util]
}
</script>

<style scoped>
.body-text {
  font-size: 16px;
}
.row-content {
  min-height: 82%;
}
.row-footer {
  min-height: 18%;
}
</style>
