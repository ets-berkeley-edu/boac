<template>
  <div class="default-margins">
    <div class="align-center d-flex pb-3">
      <v-icon
        class="mr-2 mb-2"
        color="primary"
        :icon="mdiAccountCircle"
        size="x-large"
      />
      <h1 id="page-header">Profile</h1>
    </div>
    <MyProfile />
    <div v-if="config.isDemoModeAvailable">
      <h2 class="mb-0 page-section-header-sub">Demo Mode</h2>
      <DemoModeToggle />
    </div>
  </div>
</template>

<script setup>
import DemoModeToggle from '@/components/admin/DemoModeToggle'
import MyProfile from '@/components/admin/MyProfile'
import {mdiAccountCircle} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const config = useContextStore().config
</script>
