<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner />
    <div v-if="!loading">
      <div class="align-items-center d-flex pb-3">
        <div class="pr-2">
          <font-awesome :style="{color: '#3b7ea5'}" icon="user-circle" size="2x" />
        </div>
        <div class="pt-2">
          <h1 class="page-section-header">Profile</h1>
        </div>
      </div>
      <div>
        <MyProfile />
      </div>
      <div v-if="config.isDemoModeAvailable">
        <div class="pt-4">
          <h2 class="mb-0 page-section-header-sub">Demo Mode</h2>
        </div>
        <DemoModeToggle />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DemoModeToggle from '@/components/admin/DemoModeToggle'
import MyProfile from '@/components/admin/MyProfile'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'

export default {
  name: 'Profile',
  components: {
    DemoModeToggle,
    MyProfile,
    Spinner
  },
  mixins: [Context, Util],
  mounted() {
    this.loadingComplete()
  }
}
</script>
