<template>
  <div class="default-margins">
    <h1 class="sr-only">Welcome to BOA</h1>
    <div v-if="!loading">
      <div class="mb-6">
        <div v-if="cohorts.length">
          <h2 class="page-section-header">
            Cohorts
          </h2>
          <v-expansion-panels flat multiple>
            <template v-for="cohort in cohorts" :key="cohort.id">
              <SortableGroup
                :id="`cohort-${cohort.id}`"
                :group="cohort"
                :is-cohort="true"
              />
            </template>
          </v-expansion-panels>
        </div>
        <div v-if="!cohorts.length">
          <h2 id="no-cohorts-header" class="page-section-header">
            You have no saved cohorts.
          </h2>
          <div>
            <router-link id="create-filtered-cohort" to="/cohort/new">Create a student cohort</router-link>
            automatically by your filtering preferences, such as GPA or units.
          </div>
        </div>
      </div>
      <div v-if="_filter(curatedGroups, ['domain', 'default']).length">
        <h2 class="page-section-header">Curated Groups</h2>
        <v-expansion-panels flat multiple>
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
import Util from '@/mixins/Util.vue'
import {scrollToTop} from '@/lib/utils'

export default {
  name: 'Home',
  components: {SortableGroup},
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
