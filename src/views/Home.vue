<template>
  <div class="default-margins">
    <h1 id="page-header" class="sr-only">Welcome to BOA</h1>
    <div>
      <div class="mb-6">
        <div v-if="cohorts.length">
          <h2 class="page-section-header" tabindex="-1">
            Cohorts
          </h2>
          <v-expansion-panels flat multiple>
            <SortableGroup
              v-for="cohort in cohorts"
              :id="`cohort-${cohort.id}`"
              :key="cohort.id"
              :group="cohort"
              :is-cohort="true"
            />
          </v-expansion-panels>
        </div>
        <div v-if="!cohorts.length">
          <h2 id="no-cohorts-header" class="page-section-header">
            You have no saved cohorts.
          </h2>
          <div>
            <router-link id="create-filtered-cohort" to="/cohort/new">Create a student cohort</router-link>
            automatically by your filtering preferences, such as GPA or units.
          </div>
        </div>
      </div>
      <div v-if="_filter(curatedGroups, ['domain', 'default']).length">
        <h2 class="page-section-header" tabindex="-1">Curated Groups</h2>
        <v-expansion-panels flat multiple>
          <SortableGroup
            v-for="curatedGroup in _filter(curatedGroups, ['domain', 'default'])"
            :key="curatedGroup.id"
            :group="curatedGroup"
            :is-cohort="false"
          />
        </v-expansion-panels>
      </div>
    </div>
  </div>
</template>

<script setup>
import {filter as _filter} from 'lodash'
import {onMounted, reactive} from 'vue'
import SortableGroup from '@/components/search/SortableGroup.vue'
import {getUserProfile} from '@/api/user'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const cohorts = reactive(_filter(currentUser.myCohorts, ['domain', 'default']))
const curatedGroups = reactive(_filter(currentUser.myCuratedGroups, ['domain', 'default']))

onMounted(() => {
  // The BOA homepage presents a summary of the user's cohorts and curated groups and must always be fresh.
  // If, for example, a cohort was deleted in a separate browser tab then we want this browser tab to reflect
  // that change. Therefore, we always refresh the user session object when user visits /home.
  getUserProfile().then(data => {
    contextStore.setCurrentUser(data).then()
    contextStore.loadingComplete()
  })
})
</script>
