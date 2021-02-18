<template>
  <div class="m-3">
    <Spinner />
    <div v-if="!loading">
      <h1 class="mb-4">
        Everyone's Groups
      </h1>
      <div v-if="!rows.length">
        <div>There are no saved groups</div>
      </div>
      <div v-for="(row, index) in rows" :key="index">
        <h2 class="page-section-header-sub">
          <span v-if="row.user.name">{{ row.user.name }}</span>
          <span v-if="!row.user.name">UID: {{ row.user.uid }}</span>
        </h2>
        <ul v-if="row.groups.length">
          <li v-for="group in row.groups" :key="group.id">
            <router-link :to="'/curated/' + group.id">{{ group.name }}</router-link> ({{ group.totalStudentCount }})
          </li>
        </ul>
        <div v-if="!row.groups.length" class="m-3">
          User has no groups.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {getUsersWithGroups} from '@/api/curated'
import Spinner from '@/components/util/Spinner'
import Loading from '@/mixins/Loading'
import Util from '@/mixins/Util'

export default {
  name: 'AllGroups',
  components: {Spinner},
  mixins: [Loading, Util],
  data: () => ({
    rows: []
  }),
  created() {
    getUsersWithGroups().then(data => {
      this.rows = data
      this.loaded('Everyone\'s Groups has loaded')
    })
  }
}
</script>
