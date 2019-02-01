<template>
  <div class="pl-3 pt-3">
    <Spinner/>
    <div v-if="!loading">
      <a href="#pagination-widget"
         id="skip-to-pagination-widget"
         class="sr-only"
         v-if="totalStudentCount > 50">Skip to pagination widget</a>
      <CohortPageHeader/>
      <b-collapse id="show-hide-filters"
                  class="mr-3"
                  v-model="showFilters">
        <FilterRow class="filter-row"
                   v-for="(filter, index) in filters"
                   :key="compositeKey(filter)"
                   :index="index"/>
        <FilterRow v-if="isOwnedByCurrentUser"/>
        <ApplyAndSaveButtons v-if="isOwnedByCurrentUser"/>
      </b-collapse>
      <SectionSpinner name="Students" :loading="editMode === 'apply'" />
      <div class="pt-2" v-if="showStudentsSection">
        <div class="cohort-column-results">
          <hr class="filters-section-separator mr-2"/>
          <div class="d-flex justify-content-between align-items-center p-2">
            <CuratedGroupSelector :students="students"/>
            <SortBy v-if="size(students) > 1"/>
          </div>
          <div>
            <div class="cohort-column-results">
              <div id="cohort-students" class="list-group mr-2">
                <StudentRow :student="student"
                            listType="cohort"
                            :sortedBy="preferences.sortBy"
                            :id="`student-${student.uid}`"
                            class="list-group-item student-list-item"
                            :class="{'list-group-item-info' : anchor === `#${student.uid}`}"
                            v-for="student in students"
                            :key="student.sid"/>
              </div>
            </div>
            <div class="p-3" v-if="totalStudentCount > pagination.itemsPerPage">
              <Pagination :click-handler="goToPage"
                          :init-page-number="pageNumber"
                          :limit="10"
                          :per-page="pagination.itemsPerPage"
                          :total-rows="totalStudentCount"/>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApplyAndSaveButtons from '@/components/cohort/ApplyAndSaveButtons';
import CohortEditSession from '@/mixins/CohortEditSession';
import CohortPageHeader from '@/components/cohort/CohortPageHeader';
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import FilterRow from '@/components/cohort/FilterRow';
import Loading from '@/mixins/Loading';
import Pagination from '@/components/util/Pagination';
import Scrollable from '@/mixins/Scrollable';
import SectionSpinner from '@/components/util/SectionSpinner';
import SortBy from '@/components/student/SortBy';
import Spinner from '@/components/util/Spinner';
import StudentRow from '@/components/student/StudentRow';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'Cohort',
  mixins: [CohortEditSession, Loading, Scrollable, UserMetadata, Util],
  components: {
    ApplyAndSaveButtons,
    CohortPageHeader,
    CuratedGroupSelector,
    FilterRow,
    Pagination,
    SectionSpinner,
    SortBy,
    Spinner,
    StudentRow
  },
  data: () => ({
    pageNumber: undefined,
    showFilters: undefined
  }),
  mounted() {
    const continueExistingSession =
      this.$routerHistory.hasForward() &&
      this.includes(this.$route.path, this.cohortId);
    if (continueExistingSession) {
      this.pageNumber = this.pagination.currentPage;
      this.setPageTitle(this.cohortName);
      this.loaded();
    } else {
      let id = parseInt(this.get(this.$route, 'params.id'));
      this.init({
        id: Number.isInteger(id) ? id : null,
        orderBy: this.preferences.sortBy
      }).then(() => {
        this.showFilters = !this.isCompactView;
        this.pageNumber = this.pagination.currentPage;
        this.setPageTitle(this.cohortId ? this.cohortName : 'Create Cohort');
        this.loaded();
        this.putFocusNextTick(
          this.cohortId ? 'cohort-name' : 'create-cohort-h1'
        );
      });
    }
  },
  created() {
    this.$eventHub.$on('sort-by-changed-by-user', () => this.goToPage(1));
  },
  methods: {
    compositeKey: filter => `${filter.key}${filter.value}`,
    goToPage(page) {
      this.pageNumber = page;
      this.setCurrentPage(this.pageNumber);
      this.applyFilters(this.preferences.sortBy).then(() => {
        this.scrollTo('#content');
      });
    }
  },
  computed: {
    anchor: () => location.hash,
    showStudentsSection() {
      return this.size(this.students) && this.editMode !== 'apply';
    }
  },
  watch: {
    isCompactView() {
      this.showFilters = !this.isCompactView;
    }
  }
};
</script>

<style>
.cohort-column-results {
  flex: 0 0 70%;
  flex-grow: 1;
}
.cohort-create-input-name {
  border: 1px solid #d9d9d9;
  border-color: #66afe9;
  border-radius: 4px;
  box-sizing: border-box;
  padding: 10px 10px 10px 10px;
  width: 100%;
}
.cohort-grade {
  font-weight: bold;
}
.cohort-grading-basis {
  color: #666;
  font-size: 14px;
  font-style: italic;
}
.cohort-manage-btn {
  height: 38px;
  margin: 0 0 0 5px;
}
.cohort-manage-btn-link {
  padding: 1px 0 1px 0;
}
.cohort-selector-zero-cohorts {
  color: #888;
  padding: 3px 20px 3px 20px;
  white-space: nowrap;
}
.cohort-student-bio-container {
  flex: 0.8;
  margin-left: 20px;
  min-width: 200px;
}
.filters-section-separator {
  border-top: 2px solid #eee;
  margin: 5px 0 0 0;
}
</style>

<style scoped>
.filter-row {
  align-items: center;
  background-color: #f3f3f3;
  border-left: 6px solid #3b7ea5 !important;
  margin: 5px 0 5px 0;
  padding: 2px 10px 2px 10px;
  text-align: left;
}
.student-list-item {
  border-left: none;
  border-right: none;
  display: flex;
}
</style>
