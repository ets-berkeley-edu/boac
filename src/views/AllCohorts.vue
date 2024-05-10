<template>
  <div v-if="!loading">
    <div class="mb-4">
      <h1 class="page-section-header">Everyone's Cohorts</h1>
      <div v-if="includesAdmittedStudents" class="pl-1">
        <v-icon aria-label="Star icon" class="accent-color-orange" :icon="mdiStar" />
        denotes a cohort of admitted students.
      </div>
    </div>
    <div v-if="!rows.length">
      <div>There are no saved cohorts</div>
    </div>
    <div v-for="(row, index) in rows" :key="index">
      <h2 class="page-section-header-sub">
        <span v-if="row.user.name">{{ row.user.name }}</span>
        <span v-if="!row.user.name">UID: {{ row.user.uid }}</span>
      </h2>
      <ul>
        <li v-for="cohort in row.cohorts" :key="cohort.id">
          <span v-if="cohort.domain === 'admitted_students'" class="mr-1 text-success">
            <v-icon aria-label="Star icon" class="accent-color-orange" :icon="mdiStar" />
            <span class="sr-only">Admitted Students</span>
          </span>
          <router-link :to="'/cohort/' + cohort.id">{{ cohort.name }}</router-link> ({{ cohort.totalStudentCount }})
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {mdiStar} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {getUsersWithCohorts} from '@/api/cohort'

export default {
  name: 'AllCohorts',
  mixins: [Context, Util],
  data: () => ({
    rows: [],
    includesAdmittedStudents: undefined,
  }),
  created() {
    getUsersWithCohorts().then(data => {
      this.rows = this._filter(data, row => row.cohorts.length)
      this.includesAdmittedStudents = this._find(this._flatten(this._map(this.rows, 'cohorts')), g => g.domain === 'admitted_students')
      this.loadingComplete('Everyone\'s Cohorts page has loaded')
    })
  }
}
</script>
