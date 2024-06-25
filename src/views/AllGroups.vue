<template>
  <div v-if="!loading" class="default-margins">
    <div class="mb-6">
      <h1 class="page-section-header">Everyone's Groups</h1>
      <div v-if="find(flatten(map(rows, 'groups')), g => g.domain === 'admitted_students')" class="pl-1">
        <v-icon
          aria-label="Star icon"
          color="warning"
          :icon="mdiStar"
        />
        denotes a group of admitted students.
      </div>
    </div>
    <div v-if="!rows.length">
      <div>There are no saved groups</div>
    </div>
    <div v-for="(row, index) in rows" :key="index" class="mt-4">
      <h2 class="page-section-header-sub">
        <span v-if="row.user.name">{{ row.user.name }}</span>
        <span v-if="!row.user.name">UID: {{ row.user.uid }}</span>
      </h2>
      <ul>
        <li v-for="group in row.groups" :key="group.id" class="ml-8">
          <span v-if="group.domain === 'admitted_students'" class="mr-1 text-success">
            <v-icon aria-label="Star icon" color="warning" :icon="mdiStar" />
            <span class="sr-only">Admitted Students</span>
          </span>
          <router-link :to="`/curated/${group.id}`">{{ group.name }}</router-link> ({{ group.totalStudentCount }})
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import {filter, find, flatten, map} from 'lodash'
import {getUsersWithCuratedGroups} from '@/api/curated'
import {mdiStar} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const loading = computed(() => contextStore.loading)
let rows

contextStore.loadingStart()
getUsersWithCuratedGroups().then(data => {
  rows = filter(data, row => row.groups.length)
  contextStore.loadingComplete('Everyone\'s Groups has loaded')
})
</script>
