<template>
  <div class="m-4">
    <Spinner />
    <div v-if="!loading">
      <h1 class="mb-4 page-section-header">
        Everyone's Cohorts
      </h1>
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
            <router-link :to="'/cohort/' + cohort.id">{{ cohort.name }}</router-link> ({{ cohort.totalStudentCount }})
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import {getUsersWithCohorts} from '@/api/cohort'
import Spinner from '@/components/util/Spinner'
import Loading from '@/mixins/Loading'
import Util from '@/mixins/Util'

export default {
  name: 'AllCohorts',
  components: {Spinner},
  mixins: [Loading, Util],
  data: () => ({
    rows: []
  }),
  created() {
    getUsersWithCohorts('default').then(data => {
      this.rows = this.$_.filter(data, row => row.cohorts.length)
      this.loaded('Everyone\'s Cohorts page has loaded')
    })
  }
}
</script>
