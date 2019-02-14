<template>
  <div class="home-container">
    <h1 class="sr-only">Welcome to BOAC</h1>
    <Spinner />
    <div v-if="!loading" class="home-content">
      <div>
        <div id="filtered-cohorts-header-row" class="home-page-section-header-wrapper">
          <h2 v-if="myCohorts && !size(myCohorts)" id="no-cohorts-header" class="page-section-header">
            You have no saved cohorts.
          </h2>
          <h1 v-if="myCohorts && size(myCohorts)" class="page-section-header">
            Cohorts
          </h1>
        </div>
        <div v-if="myCohorts && !size(myCohorts)">
          <router-link id="create-filtered-cohort" to="/cohort/new">Create a student cohort</router-link>
          automatically by your filtering preferences, such as GPA or units.
        </div>
        <div role="tablist" class="panel-group">
          <HomeCohort
            v-for="cohort in myCohorts"
            :key="cohort.id"
            :cohort="cohort" />
        </div>
      </div>
      <div v-if="size(myCuratedGroups)">
        <div id="curated-groups-header-row" class="home-page-section-header-wrapper">
          <h2 class="page-section-header">Curated Groups</h2>
        </div>
        <HomeCuratedGroup
          v-for="curatedGroup in myCuratedGroups"
          :key="curatedGroup.id"
          :curated-group="curatedGroup" />
      </div>
    </div>
  </div>
</template>

<script>
import HomeCohort from '@/components/home/HomeCohort.vue';
import HomeCuratedGroup from '@/components/home/HomeCuratedGroup.vue';
import Loading from '@/mixins/Loading.vue';
import Spinner from '@/components/util/Spinner.vue';
import UserMetadata from '@/mixins/UserMetadata.vue';
import Util from '@/mixins/Util.vue';

export default {
  name: 'Home',
  components: {
    HomeCohort,
    HomeCuratedGroup,
    Spinner
  },
  mixins: [Loading, UserMetadata, Util],
  watch: {
    myCohorts: function() {
      if (this.myCohorts) {
        this.loaded();
      }
    },
    myCuratedGroups: function() {
      if (this.myCuratedGroups) {
        this.loaded();
      }
    }
  },
  mounted() {
    if (this.myCohorts || this.myCuratedGroups) {
      this.loaded();
    }
  }
};
</script>

<style scoped>
.home-container {
  padding: 0 0 0 20px;
  width: 100%;
}
.home-content {
  display: flex;
  flex-direction: column;
}
.home-page-section-header-wrapper {
  display: flex;
}
.panel-group {
  margin-bottom: 20px;
}
</style>
