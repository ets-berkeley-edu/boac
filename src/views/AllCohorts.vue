<template>
  <div class="m-2">
    <Spinner />
    <div v-if="!loading">
      <h1 ref="pageHeader" tabindex="0">Everyone's Cohorts</h1>

      <div v-if="!usersWithCohorts.length">
        <div>There are no saved cohorts</div>
      </div>
      <div v-for="owner in usersWithCohorts" :key="owner.uid">
        <h2 class="page-section-header-sub">
          <span v-if="owner.name">{{ owner.name }}</span>
          <span v-if="!owner.name">UID: {{ owner.uid }}</span>
        </h2>
        <ul>
          <li v-for="cohort in owner.cohorts" :key="cohort.id">
            <router-link :to="'/cohort/' + cohort.id">{{ cohort.name }}</router-link> ({{ cohort.totalStudentCount }})
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { getUsersWithCohorts } from '@/api/cohort';
import Spinner from '@/components/util/Spinner';
import Loading from '@/mixins/Loading';

export default {
  name: 'AllCohorts',
  components: { Spinner },
  mixins: [Loading],
  data: () => ({
    usersWithCohorts: []
  }),
  created() {
    getUsersWithCohorts().then(data => {
      this.usersWithCohorts = data;
      this.loaded();
    });
  }
};
</script>
