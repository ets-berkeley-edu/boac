<template>
  <div class="ml-3 mt-3">
    <h1 class="sr-only">Welcome to BOA</h1>
    <Spinner />
    <div v-if="!loading" class="home-content">
      <div>
        <div id="filtered-cohorts-header-row">
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
        <div id="curated-groups-header-row">
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
import Scrollable from '@/mixins/Scrollable';
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
  mixins: [Loading, Scrollable, UserMetadata, Util],
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
      this.scrollToTop();
    }
  }
};
</script>

<style scoped>
.home-content {
  display: flex;
  flex-direction: column;
}
.panel-group {
  margin-bottom: 20px;
}
</style>

<style>
.accordion .panel-title a:focus,
.accordion .panel-title a:hover {
  text-decoration: none;
}
.accordion-header {
  margin: 0;
}
.accordion-heading-caret {
  color: #337ab7;
  margin-right: 15px;
  width: 10px;
}
.accordion-heading {
  background: #ecf5fb;
  display: flex;
  justify-content: space-between;
}
.accordion-heading-count {
  align-items: center;
  display: flex;
  justify-content: flex-end;
  margin: 10px 15px;
  min-width: 130px;
}
.accordion-heading-count-label {
  margin: 0 5px;
}
.accordion-heading-name {
  align-items: center;
  display: flex;
  margin: 10px 15px;
}
.accordion-heading-link:active,
.accordion-heading-link:focus,
.accordion-heading-link:hover {
  text-decoration: none;
}
.home-inactive-info-icon {
  color: #d0021b;
  font-size: 16px;
}
.home-issues-pill {
  border-radius: 10px;
  color: #fff;
  display: inline-block;
  font-size: 16px;
  font-weight: 800;
  height: 20px;
  line-height: 20px;
  padding: 0 4px 0 4px;
  text-align: center;
}
.home-issues-pill-nonzero {
  background-color: #f0ad4e;
}
.home-issues-pill-zero {
  background-color: #ccc;
}
</style>
