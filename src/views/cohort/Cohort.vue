<template>
  <div class="p-3">
    <Spinner/>
    <div v-if="!loading">
      <a href="#pagination-widget"
         id="skip-to-pagination-widget"
         class="sr-only"
         v-if="totalStudentCount > 50">Skip to pagination widget</a>
      <CohortPageHeader />
      <b-collapse id="show-hide-filters" v-model="showFilters">
        <FilterRow class="filter-row"
                   v-for="(filter, index) in filters"
                   :key="compositeKey(filter)"
                   :index="index"/>
        <FilterRow />
        <ApplyAndSaveButtons />
      </b-collapse>
      <SectionSpinner name="Students" :loading="editMode === 'apply'" />
      <div v-if="showStudentsSection">
        <div class="cohort-column-results">
          <div class="search-header-curated-cohort">
            <CuratedGroupSelector :students="students"/>
          </div>
          <div>
            <Students :listName="cohortName"
                      listType="cohort"
                      :students="students"></Students>
            <div class="course-pagination">
              <b-pagination id="pagination-widget"
                            size="md"
                            :total-rows="totalStudentCount"
                            :limit="20"
                            v-model="pageNumber"
                            :per-page="pagination.itemsPerPage"
                            :hide-goto-end-buttons="true"
                            v-if="totalStudentCount > pagination.itemsPerPage"
                            @input="nextPage()">
              </b-pagination>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import ApplyAndSaveButtons from '@/components/cohort/ApplyAndSaveButtons';
import CohortEditSession from '@/mixins/CohortEditSession';
import CohortPageHeader from '@/components/cohort/CohortPageHeader';
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import FilterRow from '@/components/cohort/FilterRow';
import Loading from '@/mixins/Loading';
import SectionSpinner from '@/components/util/SectionSpinner';
import Spinner from '@/components/util/Spinner';
import Students from '@/components/student/Students';

export default {
  name: 'Cohort',
  mixins: [CohortEditSession, Loading],
  components: {
    ApplyAndSaveButtons,
    CohortPageHeader,
    CuratedGroupSelector,
    FilterRow,
    SectionSpinner,
    Spinner,
    Students
  },
  data: () => ({
    pageNumber: undefined,
    showFilters: undefined
  }),
  created() {
    let id = _.get(this.$route, 'params.id');
    let encodedCriteria = _.get(this.$route, 'query.q');
    this.initSession(id, encodedCriteria).then(() => {
      this.showFilters = !this.isCompactView;
      this.currentPage = this.pagination.currentPage;
      this.loaded();
    });
  },
  methods: {
    compositeKey: filter => `${filter.key}${filter.value}`,
    nextPage() {
      this.setCurrentPage(this.pageNumber);
      this.applyFilters();
    }
  },
  computed: {
    showStudentsSection() {
      return _.size(this.students) && this.editMode !== 'apply';
    }
  },
  watch: {
    isCompactView() {
      this.showFilters = !this.isCompactView;
    }
  }
};
</script>

<style scoped>
.filter-row {
  align-items: center;
  background-color: #f3f3f3;
  border-left: 6px solid #3b7ea5 !important;
  margin: 5px 0 5px 0;
  padding: 2px 10px 2px 10px;
  text-align: left;
}
</style>
