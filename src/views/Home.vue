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
            <template v-for="cohort in cohorts" :key="cohort.id">
              <SortableGroup
                :id="`cohort-${cohort.id}`"
                :group="cohort"
                :is-cohort="true"
              />
            </template>
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
          <template
            v-for="curatedGroup in _filter(curatedGroups, ['domain', 'default'])"
            :key="curatedGroup.id"
          >
            <SortableGroup :group="curatedGroup" :is-cohort="false" />
          </template>
        </v-expansion-panels>
      </div>
    </div>
  </div>
</template>

<script setup>
import SortableGroup from '@/components/search/SortableGroup.vue'
import {getUserProfile} from '@/api/user'
import {filter as _filter} from 'lodash'
import {onMounted, reactive} from 'vue'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const cohorts = reactive(_filter(currentUser.myCohorts, ['domain', 'default']))
const curatedGroups = reactive(_filter(currentUser.myCuratedGroups, ['domain', 'default']))

onMounted(() => {
  if (contextStore.currentUser.isStale) {
    contextStore.loadingStart()
    getUserProfile().then(data => {
      contextStore.setCurrentUser(data)
      contextStore.currentUser.isStale = true
      contextStore.loadingComplete()
    })
  } else {
    contextStore.currentUser.isStale = true
    contextStore.loadingComplete()
  }
})
</script>
