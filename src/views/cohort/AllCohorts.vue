<template>
  <div class="m-3">
    <Spinner/>
    <div v-if="!loading">
      <h1>Everyone's Cohorts</h1>

      <div v-if="!usersWithCohorts.length">
        <div>There are no saved cohorts</div>
      </div>
      <div v-for="owner in usersWithCohorts" v-bind:key="owner.uid">
        <h2 class="page-section-header-sub">{{owner.firstName}} {{owner.lastName}}</h2>
        <ul>
          <li v-for="cohort in owner.cohorts" v-bind:key="cohort.id">
            <router-link :to="'/cohort/' + cohort.id">{{ cohort.name }}</router-link> ({{ cohort.totalStudentCount }})
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { getUsersWithCohorts } from '@/api/cohort';
import Spinner from '@/components/Spinner.vue';
import Loading from '@/mixins/Loading.vue';

export default {
  name: 'AllCohorts',
  mixins: [Loading],
  components: { Spinner },
  created() {
    getUsersWithCohorts().then(data => {
      this.usersWithCohorts = data;
      this.loaded();
    });
  },
  data: () => ({
    usersWithCohorts: []
  })
};
</script>
