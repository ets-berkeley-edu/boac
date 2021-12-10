<template>
  <div class="ml-3 mt-3">
    <h1 class="sr-only">Welcome to BOA</h1>
    <Spinner />
    <div v-if="!loading" class="home-content">
      <div>
        <div id="filtered-cohorts-header-row">
          <h2 v-if="!$currentUser.myCohorts.length" id="no-cohorts-header" class="page-section-header">
            You have no saved cohorts.
          </h2>
          <h2 v-if="$currentUser.myCohorts.length" class="page-section-header">
            Cohorts
          </h2>
        </div>
        <div v-if="!$currentUser.myCohorts.length">
          <router-link id="create-filtered-cohort" to="/cohort/new">Create a student cohort</router-link>
          automatically by your filtering preferences, such as GPA or units.
        </div>
        <div class="panel-group">
          <SortableGroup
            v-for="cohort in $currentUser.myCohorts"
            :key="cohort.id"
            :group="cohort"
            :is-cohort="true"
          />
        </div>
      </div>
      <div v-if="$currentUser.myCuratedGroups.length">
        <div id="curated-groups-header-row">
          <h2 class="page-section-header">Curated Groups</h2>
        </div>
        <SortableGroup
          v-for="curatedGroup in $currentUser.myCuratedGroups"
          :key="curatedGroup.id"
          :group="curatedGroup"
          :is-cohort="false"
        />
      </div>
    </div>
  </div>
</template>

<script>
import Loading from '@/mixins/Loading.vue'
import Scrollable from '@/mixins/Scrollable'
import SortableGroup from '@/components/search/SortableGroup.vue'
import Spinner from '@/components/util/Spinner.vue'
import Util from '@/mixins/Util.vue'

export default {
  name: 'Home',
  components: {
    SortableGroup,
    Spinner
  },
  mixins: [Loading, Scrollable, Util],
  mounted() {
    this.loaded('BOA has loaded')
    this.scrollToTop()
  }
}
</script>

<style scoped>
.home-content {
  display: flex;
  flex-direction: column;
}
</style>
