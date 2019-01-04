<template>
  <div class="p-3">
    <Spinner/>
    <div v-if="!loading">
      <a href="#pagination-widget"
         id="skip-to-pagination-widget"
         class="sr-only"
         v-if="totalStudentCount > 50">Skip to pagination widget</a>
      <CohortPageHeader />
      <div v-if="!isCompactView">
        <CohortFilter class="cohort-filter-row"
                      v-for="(filter, index) in filters" :key="index"
                      :filter="filter"
                      :index="index"/>
        <AddCohortFilterMenu />
      </div>
      <div v-if="students.length">
        <div class="cohort-column-results">
          <div class="search-header-curated-cohort">
            <CuratedGroupSelector :students="students"/>
          </div>
          <div>
            <Students :listName="cohortName"
                      listType="cohort"
                      :students="students"></Students>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import AddCohortFilterMenu from '@/components/cohort/AddCohortFilterMenu';
import CohortEditSession from '@/mixins/CohortEditSession';
import CohortFilter from '@/components/cohort/CohortFilter';
import CohortPageHeader from '@/components/cohort/CohortPageHeader';
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/Spinner';
import Students from '@/components/student/Students';

export default {
  name: 'Cohort',
  mixins: [CohortEditSession, Loading],
  components: {
    AddCohortFilterMenu,
    CohortFilter,
    CohortPageHeader,
    CuratedGroupSelector,
    Spinner,
    Students
  },
  created() {
    let id = _.get(this.$route, 'params.id');
    let encodedCriteria = _.get(this.$route, 'query.q');
    this.initSession(id, encodedCriteria).then(() => {
      this.loaded();
    });
  }
};
</script>

<style>
.disabled-link {
  color: lightgrey;
}
</style>
