<template>
  <div class="p-3">
    <Spinner/>
    <div v-if="!loading">
      <a href="#pagination-widget"
         id="skip-to-pagination-widget"
         class="sr-only"
         v-if="totalStudentCount > 50">Skip to pagination widget</a>
      <CohortPageHeader />
      <CohortFilter class="cohort-filter-row"
                    v-for="(filter, index) in filters" :key="index"
                    :filter="filter"
                    :index="index"/>
      <Students :listName="cohortName"
                listType="cohort"
                :students="students"></Students>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import CohortEditSession from '@/mixins/CohortEditSession';
import CohortFilter from '@/components/cohort/CohortFilter';
import CohortPageHeader from '@/components/cohort/CohortPageHeader';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/Spinner';
import Students from '@/components/student/Students';

export default {
  name: 'Cohort',
  mixins: [CohortEditSession, Loading],
  components: {
    Spinner,
    CohortFilter,
    CohortPageHeader,
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
