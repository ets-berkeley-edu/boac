<template>
  <div class="home-container">
    <Spinner/>
    <div class="home-content" v-if="!loading">
      <div>
        <div id="filtered-cohorts-header-row" class="home-page-section-header-wrapper">
          <h1 class="page-section-header" v-if="myCohorts && !size(myCohorts)">
            You have no saved cohorts.
          </h1>
          <h1 class="page-section-header" v-if="myCohorts && size(myCohorts)">
            Cohorts
          </h1>
        </div>
        <div v-if="myCohorts && !size(myCohorts)">
          <router-link id="create-filtered-cohort" to="/create_cohort">Create a student cohort</router-link>
          automatically by your filtering preferences, such as GPA or units.
        </div>
        <div role="tablist" class="panel-group">
          <HomeCohort v-for="(cohort, index) in myCohorts" 
                      :key="index" 
                      :cohort="cohort" 
                      :index="index"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import HomeCohort from '@/components/home/HomeCohort.vue';
import Loading from '@/mixins/Loading.vue';
import Spinner from '@/components/util/Spinner.vue';
import UserMetadata from '@/mixins/UserMetadata.vue';
import Util from '@/mixins/Util.vue';

export default {
  name: 'Home',
  mixins: [Loading, UserMetadata, Util],
  components: {
    HomeCohort,
    Spinner
  },
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
  }
};
</script>
