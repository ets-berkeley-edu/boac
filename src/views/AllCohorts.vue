<template>
  <div v-if="!loading" class="default-margins">
    <div class="mb-8">
      <h1 class="page-section-header">Everyone's Cohorts</h1>
      <div v-if="includesAdmittedStudents" class="pl-1">
        <v-icon
          aria-label="Star icon"
          color="warning"
          :icon="mdiStar"
        />
        denotes a cohort of admitted students.
      </div>
    </div>
    <div v-if="!rows.length">
      <div>There are no saved cohorts</div>
    </div>
    <div v-for="(row, index) in rows" :key="index" class="mt-4">
      <h2 class="page-section-header-sub">
        <span v-if="row.user.name">{{ row.user.name }}</span>
        <span v-if="!row.user.name">UID: {{ row.user.uid }}</span>
      </h2>
      <ul>
        <li v-for="cohort in row.cohorts" :key="cohort.id" class="ml-8">
          <span v-if="cohort.domain === 'admitted_students'" class="mr-1 text-success">
            <v-icon aria-label="Star icon" color="warning" :icon="mdiStar" />
            <span class="sr-only">Admitted Students</span>
          </span>
          <router-link :to="'/cohort/' + cohort.id">{{ cohort.name }}</router-link> ({{ cohort.totalStudentCount }})
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import {filter as _filter, find, flatten, map} from 'lodash'
import {getUsersWithCohorts} from '@/api/cohort'
import {mdiStar} from '@mdi/js'
import {useContextStore} from '@/stores/context'

let includesAdmittedStudents = undefined
const loading = computed(() => useContextStore().loading)
let rows = []

getUsersWithCohorts().then(data => {
  rows = _filter(data, row => row.cohorts.length)
  includesAdmittedStudents = find(flatten(map(rows, 'cohorts')), g => g.domain === 'admitted_students')
  useContextStore().loadingComplete('Everyone\'s Cohorts loaded')
})
</script>
