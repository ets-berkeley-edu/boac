<template>
  <div class="ml-6 mt-6">
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
        <v-expansion-panels
          elevation="0"
          multiple
        >
          <template v-for="cohort in cohorts" :key="cohort.id">
            <SortableGroup
              :id="`cohort-${cohort.id}`"
              :group="cohort"
              :is-cohort="true"
            />
          </template>
        </v-expansion-panels>
      </div>
      <div v-if="_filter(curatedGroups, ['domain', 'default']).length">
        <div id="curated-groups-header-row">
          <h2 class="page-section-header">Curated Groups</h2>
        </div>
        <v-expansion-panels
          elevation="0"
          multiple
          variant="accordion"
        >
          <template
            v-for="curatedGroup in _filter(curatedGroups, ['domain', 'default'])"
            :key="curatedGroup.id"
          >
            <SortableGroup :group="curatedGroup" :is-cohort="false" />
          </template>
        </v-expansion-panels>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import SortableGroup from '@/components/search/SortableGroup.vue'
import Spinner from '@/components/util/Spinner.vue'
import Util from '@/mixins/Util.vue'
import {scrollToTop} from '@/lib/utils'

export default {
  name: 'Home',
  components: {SortableGroup, Spinner},
  mixins: [Context, Util],
  computed: {
    cohorts() {
      return this._filter(this.currentUser.myCohorts, ['domain', 'default'])
    },
    curatedGroups() {
      return this._filter(this.currentUser.myCuratedGroups, ['domain', 'default'])
    },
  },
  mounted() {
    this.loadingComplete()
    scrollToTop()
  }
}
</script>

<style scoped>
.home-content {
  display: flex;
  flex-direction: column;
}
</style>
