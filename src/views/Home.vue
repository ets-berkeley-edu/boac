<template>
  <div class="ml-4 mt-4">
    <h1 class="sr-only">Welcome to BOA</h1>
    <Spinner />
    <div v-if="!loading" class="home-content">
      <div class="pb-2">
        <div id="filtered-cohorts-header-row">
          <h2 v-if="!cohorts.length" id="no-cohorts-header" class="page-section-header">
            You have no saved cohorts.
          </h2>
          <h2 v-if="cohorts.length" class="page-section-header">
            Cohorts
          </h2>
        </div>
        <div v-if="!cohorts.length" class="mb-3">
          <router-link id="create-filtered-cohort" to="/cohort/new">Create a student cohort</router-link>
          automatically by your filtering preferences, such as GPA or units.
        </div>
        <div v-for="cohort in cohorts" :key="cohort.id">
          <SortableGroup :group="cohort" :is-cohort="true" />
        </div>
      </div>
      <div v-if="_filter(curatedGroups, ['domain', 'default']).length">
        <div id="curated-groups-header-row">
          <h2 class="page-section-header">Curated Groups</h2>
        </div>
        <div
          v-for="curatedGroup in _filter(curatedGroups, ['domain', 'default'])"
          :key="curatedGroup.id"
        >
          <SortableGroup :group="curatedGroup" :is-cohort="false" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading.vue'
import Scrollable from '@/mixins/Scrollable'
import SortableGroup from '@/components/search/SortableGroup.vue'
import Spinner from '@/components/util/Spinner.vue'
import Util from '@/mixins/Util.vue'

export default {
  name: 'Home',
  mixins: [Context, Loading, Scrollable, Util],
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
    this.cohorts = this._filter(this.currentUser.myCohorts, ['domain', 'default'])
    this.curatedGroups = this._filter(this.currentUser.myCuratedGroups, ['domain', 'default'])
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
