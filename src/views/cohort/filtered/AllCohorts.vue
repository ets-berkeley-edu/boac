<template>
  <div class="all-cohorts-container">
    <Spinner/>
    <div v-if="!loading">
      <h1 class="page-section-header">Everyone's Cohorts</h1>

      <div v-if="!usersWithCohorts.length">
        <div>There are no saved cohorts</div>
      </div>
      <div v-for="owner in usersWithCohorts" v-bind:key="owner.uid">
        <h2 class="page-section-header-sub">{{owner.firstName}} {{owner.lastName}}</h2>
        <ul>
          <li v-for="cohort in owner.cohorts" v-bind:key="cohort.id">
            <SmartRef :path="'/cohort/filtered?id=' + cohort.id">{{ cohort.name }}</SmartRef> ({{ cohort.totalStudentCount }})
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { getUsersWithCohorts } from '@/api/cohorts';
import Spinner from '@/components/Spinner.vue';
import Loading from '@/mixins/Loading.vue';
import SmartRef from '@/components/SmartRef';

export default {
  name: 'AllCohorts',
  mixins: [Loading],
  components: {
    SmartRef,
    Spinner
  },
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

<style scoped>
.all-cohorts-container {
  padding: 0 10px 0 10px;
}
</style>
