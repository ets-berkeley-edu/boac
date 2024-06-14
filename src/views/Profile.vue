<template>
  <div v-if="!useContextStore().loading" class="default-margins">
    <div class="align-center d-flex pb-3">
      <v-icon
        class="mr-2 text-primary"
        :icon="mdiAccountCircle"
        size="x-large"
      />
      <h1 class="mt-2 page-section-header">Profile</h1>
    </div>
    <MyProfile />
    <div v-if="isDemoModeAvailable">
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

const contextStore = useContextStore()
const isDemoModeAvailable = contextStore.config.isDemoModeAvailable
contextStore.loadingComplete()
</script>
