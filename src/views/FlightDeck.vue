<template>
  <div class="default-margins">
    <div class="align-center d-flex pb-3">
      <v-icon
        :icon="mdiAirplaneTakeoff"
        class="mr-3 mb-2"
        color="primary"
        size="x-large"
      />
      <div class="d-flex align-center">
        <h1 id="page-header">BOA v{{ BOA.version }} Flight Deck</h1>
        <a
          v-if="get(BOA, 'build.gitCommit')"
          class="mb-2 ml-3"
          :href="`https://github.com/ets-berkeley-edu/boac/commit/${BOA.build.gitCommit}`"
          target="_blank"
        >
          <span class="sr-only">Github commit {{ BOA.build.gitCommit }}</span>
          <v-icon :icon="mdiGithub" />
        </a>
      </div>
    </div>
    <div v-if="config.isDemoModeAvailable" class="mb-4">
      <h2 class="mb-2 page-section-header-sub text-primary">Demo Mode</h2>
      <DemoModeToggle />
    </div>
    <div class="mb-8">
      <h2 id="edit-service-announcement" class="page-section-header-sub text-primary">Service Alert</h2>
      <div class="mx-2">
        <EditServiceAnnouncement />
      </div>
    </div>
    <div>
      <h2 id="manage-topics-header" class="mb-4 page-section-header-sub text-primary">Manage Topics</h2>
      <div class="ml-2">
        <ManageTopics />
      </div>
    </div>
    <div class="mb-3 mt-10">
      <h2 class="page-section-header-sub text-primary">Configs</h2>
    </div>
    <v-table density="compact" hover>
      <tbody>
        <tr v-for="key in Object.keys(config).sort()" :key="key">
          <td class="pl-0">{{ key }}</td>
          <td>{{ config[key] || '&mdash;' }}</td>
        </tr>
      </tbody>
    </v-table>
  </div>
</template>

<script setup>
import DemoModeToggle from '@/components/admin/DemoModeToggle'
import EditServiceAnnouncement from '@/components/admin/EditServiceAnnouncement'
import ManageTopics from '@/components/topics/ManageTopics'
import {getVersion} from '@/api/config'
import {mdiAirplaneTakeoff, mdiGithub} from '@mdi/js'
import {onMounted} from 'vue'
import {useContextStore} from '@/stores/context'
import {get} from 'lodash'

let BOA = {}
const contextStore = useContextStore()
const config = contextStore.config

contextStore.loadingStart()
onMounted(() => getVersion().then(data => {
  BOA = data
  contextStore.loadingComplete()
}))
</script>
