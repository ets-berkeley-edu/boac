<template>
  <div>
    <h2>Filtered Cohorts</h2>
    <ul v-if="user">
      <li v-for="c in user.myFilteredCohorts" v-bind:key="c.id">
        <span>{{ c.name }}</span>
      </li>
    </ul>
    <h2>Curated Cohorts</h2>
    <ul v-if="user">
      <li v-for="c in user.myCuratedCohorts" v-bind:key="c.id">
        <SmartRouteRef data-uri="'/cohort/curated/' + c.id">{{ c.name }}</SmartRouteRef>
      </li>
    </ul>
  </div>
</template>

<script>
import store from '@/store';
import SmartRouteRef from '@/components/SmartRouteRef.vue';

export default {
  name: 'Sidebar',
  components: {
    SmartRouteRef
  },
  computed: {
    user() {
      return store.getters.user;
    }
  }
};
</script>
