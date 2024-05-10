<template>
  <div v-if="!loading">
    <div class="mb-4">
      <h1 class="page-section-header">Everyone's Groups</h1>
      <div v-if="_find(_flatten(_map(rows, 'groups')), g => g.domain === 'admitted_students')" class="pl-1">
        <v-icon aria-label="Star icon" class="accent-color-orange" :icon="mdiStar" />
        denotes a group of admitted students.
      </div>
    </div>
    <div v-if="!rows.length">
      <div>There are no saved groups</div>
    </div>
    <div v-for="(row, index) in rows" :key="index">
      <h2 class="page-section-header-sub">
        <span v-if="row.user.name">{{ row.user.name }}</span>
        <span v-if="!row.user.name">UID: {{ row.user.uid }}</span>
      </h2>
      <ul>
        <li v-for="group in row.groups" :key="group.id">
          <span v-if="group.domain === 'admitted_students'" class="mr-1 text-success">
            <v-icon aria-label="Star icon" class="accent-color-orange" :icon="mdiStar" />
            <span class="sr-only">Admitted Students</span>
          </span>
          <router-link :to="'/curated/' + group.id">{{ group.name }}</router-link> ({{ group.totalStudentCount }})
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
import {getUsersWithCuratedGroups} from '@/api/curated'

export default {
  name: 'AllGroups',
  mixins: [Context, Util],
  data: () => ({
    rows: []
  }),
  created() {
    getUsersWithCuratedGroups().then(data => {
      this.rows = this._filter(data, row => row.groups.length)
      this.loadingComplete('Everyone\'s Groups has loaded')
    })
  }
}
</script>
