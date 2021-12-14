<template>
  <div class="ml-3 mt-3">
    <h1 class="sr-only">Welcome to BOA</h1>
    <Spinner />
    <div v-if="!loading" class="home-content">
      <div class="pb-3">
        <div id="filtered-cohorts-header-row">
          <h2 v-if="!cohorts.length" id="no-cohorts-header" class="page-section-header">
            You have no saved cohorts.
          </h2>
          <h2 v-if="cohorts.length" class="page-section-header">
            Cohorts
          </h2>
        </div>
        <div v-if="!cohorts.length">
          <router-link id="create-filtered-cohort" to="/cohort/new">Create a student cohort</router-link>
          automatically by your filtering preferences, such as GPA or units.
        </div>
        <div v-for="cohort in cohorts" :key="cohort.id" class="mb-2">
          <SortableGroup :group="cohort" :is-cohort="true" />
        </div>
      </div>
      <div v-if="$_.filter(curatedGroups, ['domain', 'default']).length" class="pb-3">
        <div id="curated-groups-header-row">
          <h2 class="page-section-header">Curated Groups</h2>
        </div>
        <div
          v-for="curatedGroup in $_.filter(curatedGroups, ['domain', 'default'])"
          :key="curatedGroup.id"
          class="mb-2"
        >
          <SortableGroup :group="curatedGroup" :is-cohort="false" />
        </div>
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
  mixins: [Loading, Scrollable, Util],
  components: {
    SortableGroup,
    Spinner
  },
  data: () => ({
    cohorts: undefined,
    curatedGroups: undefined
  }),
  mounted() {
    this.loaded('Home loaded')
    this.cohorts = this.$_.filter(this.$currentUser.myCohorts, ['domain', 'default'])
    this.curatedGroups = this.$_.filter(this.$currentUser.myCuratedGroups, ['domain', 'default'])
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
