<template>
  <div v-if="!useContextStore().loading" class="default-margins">
    <div class="align-center d-flex pb-3">
      <div class="pr-2 pt-1">
        <v-icon :style="{color: '#3b7ea5'}" :icon="mdiAccountCircle" size="x-large" />
      </div>
      <div class="pt-2">
        <h1 class="page-section-header">Profile</h1>
      </div>
    </div>
    <div>
      <MyProfile />
    </div>
    <div v-if="useContextStore().config.isDemoModeAvailable">
      <div class="pt-4">
        <h2 class="mb-0 page-section-header-sub">Demo Mode</h2>
      </div>
      <DemoModeToggle />
    </div>
  </div>
</template>

<script setup>
import {mdiAccountCircle} from '@mdi/js'
</script>

<script>
import {useContextStore} from '@/stores/context'
import DemoModeToggle from '@/components/admin/DemoModeToggle'
import MyProfile from '@/components/admin/MyProfile'

export default {
  name: 'Profile',
  components: {
    DemoModeToggle,
    MyProfile
  },
  mounted() {
    useContextStore().loadingComplete()
  }
}
</script>
