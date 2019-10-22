<template>
  <div class="ml-3 mt-3">
    <Spinner alert-prefix="Cohort" />
    <div v-if="!loading">
      <div class="sr-only" aria-live="polite">{{ screenReaderAlert }}</div>
      <CohortPageHeader />
      <b-collapse
        id="show-hide-filters"
        v-model="showFilters"
        class="mr-3">
        <FilterRow
          v-for="(filter, index) in filters"
          :key="filterRowUniqueKey(filter, index)"
          class="filter-row"
          :index="index" />
        <FilterRow v-if="isOwnedByCurrentUser" />
        <ApplyAndSaveButtons v-if="isOwnedByCurrentUser" />
      </b-collapse>
      <SectionSpinner name="Students" :loading="editMode === 'apply'" />
      <div v-if="showStudentsSection" class="pt-2">
        <a
          v-if="totalStudentCount > 50"
          id="skip-to-pagination-widget"
          class="sr-only"
          href="#pagination-widget"
          @click="screenReaderAlert = 'Go to another page of search results'">Skip to bottom, other pages of search results</a>
        <div class="cohort-column-results">
          <hr class="filters-section-separator mr-2" />
          <div class="d-flex justify-content-between align-items-center p-2">
            <CuratedGroupSelector
              :context-description="`Cohort ${cohortName || ''}`"
              :ga-event-tracker="gaCohortEvent"
              :students="students" />
            <SortBy v-if="showSortBy" />
          </div>
          <div>
            <div class="cohort-column-results">
              <div id="cohort-students" class="list-group mr-2">
                <StudentRow
                  v-for="(student, index) in students"
                  :id="`student-${student.uid}`"
                  :key="student.sid"
                  :row-index="index"
                  :student="student"
                  list-type="cohort"
                  :sorted-by="preferences.sortBy"
                  class="list-group-item border-left-0 border-right-0"
                  :class="{'list-group-item-info' : anchor === `#${student.uid}`}" />
              </div>
            </div>
            <div v-if="totalStudentCount > pagination.itemsPerPage" class="p-3">
              <Pagination
                :click-handler="goToPage"
                :init-page-number="pageNumber"
                :limit="10"
                :per-page="pagination.itemsPerPage"
                :total-rows="totalStudentCount" />
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
  mixins: [
    CohortEditSession,
    Loading,
    Scrollable,
    UserMetadata,
    Util
  ],
  data: () => ({
    pageNumber: undefined,
    screenReaderAlert: undefined,
    showFilters: undefined
  }),
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
  },
  mounted() {
    const forwardPath = this.$routerHistory.hasForward() && this.get(this.$routerHistory.next(), 'path');
    const continueExistingSession = this.startsWith(forwardPath, '/student') && this.size(this.filters);
    if (continueExistingSession) {
      this.showFilters = !this.isCompactView;
      this.pageNumber = this.pagination.currentPage;
      this.setPageTitle(this.cohortName);
      this.loaded();
    } else {
      const id = this.toInt(this.get(this.$route, 'params.id'));
      this.init({
        id,
        orderBy: this.preferences.sortBy
      }).then(() => {
        this.showFilters = !this.isCompactView;
        this.pageNumber = this.pagination.currentPage;
        this.setPageTitle(this.cohortId ? this.cohortName : 'Create Cohort');
        this.loaded();
        this.putFocusNextTick(
          this.cohortId ? 'cohort-name' : 'create-cohort-h1'
        );
        this.gaCohortEvent({
          id: this.cohortId || '',
          name: this.cohortName || '',
          action: 'view'
        });
      });
    }
  },
  created() {
    this.$eventHub.$on('cohort-apply-filters', () => {
      this.setPagination(1);
    });
    this.$eventHub.$on('sortBy-user-preference-change', sortBy => {
      if (!this.loading) {
        this.goToPage(1);
        this.screenReaderAlert = `Sort students by ${sortBy}`;
        this.gaCohortEvent({
          id: this.cohortId || '',
          name: this.cohortName || '',
          action: this.screenReaderAlert
        });
      }
    });
  },
  methods: {
    filterRowUniqueKey: (filter, index) => `${filter.key}-${index}`,
    goToPage(page) {
      if (page > 1) {
        this.screenReaderAlert = `Go to page ${page}`;
        this.gaCohortEvent({
          id: this.cohortId || '',
          name: this.cohortName || '',
          action: this.screenReaderAlert
        });
      }
      this.setPagination(page);
      this.onPageNumberChange().then(this.scrollToTop);
    },
    setPagination(page) {
      this.pageNumber = page;
      this.setCurrentPage(this.pageNumber);
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
.cohort-grading-basis {
  color: #666;
  font-size: 14px;
  font-style: italic;
}
.cohort-manage-btn {
  height: 38px;
  margin: 0 0 0 5px;
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
}
</style>
