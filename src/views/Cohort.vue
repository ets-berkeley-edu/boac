<template>
  <div class="ml-3 mt-3">
    <Spinner :alert-prefix="!cohortId && totalStudentCount === undefined ? 'Create cohort page' : cohortName" />
    <div v-if="!loading">
      <CohortPageHeader :show-history="showHistory" :toggle-show-history="toggleShowHistory" />
      <b-collapse
        id="show-hide-filters"
        v-model="showFilters"
        class="mr-3">
        <FilterRow
          v-for="(filter, index) in filters"
          :key="filterRowUniqueKey(filter, index)"
          :index="index"
          class="filter-row" />
        <FilterRow v-if="isOwnedByCurrentUser" />
        <ApplyAndSaveButtons v-if="isOwnedByCurrentUser" />
      </b-collapse>
      <hr class="filters-section-separator mr-2 mt-3" />
      <SectionSpinner :loading="editMode === 'apply'" name="Students" />
      <div v-if="!showHistory && showStudentsSection">
        <a
          v-if="totalStudentCount > 50"
          id="skip-to-pagination-widget"
          class="sr-only"
          href="#pagination-widget"
          @click="alertScreenReader('Go to another page of search results')"
          @keyup.enter="alertScreenReader('Go to another page of search results')">Skip to bottom, other pages of search results</a>
        <div class="cohort-column-results">
          <div v-if="domain === 'default'" class="d-flex justify-content-between align-items-center p-2">
            <CuratedGroupSelector
              :context-description="`Cohort ${cohortName || ''}`"
              :ga-event-tracker="$ga.cohortEvent"
              :on-create-curated-group="resetFiltersToLastApply"
              :students="students" />
            <SortBy v-if="showSortBy" />
          </div>
          <div>
            <div class="cohort-column-results">
              <div v-if="domain === 'default'" id="cohort-students" class="list-group mr-2">
                <StudentRow
                  v-for="(student, index) in students"
                  :id="`student-${student.uid}`"
                  :key="student.sid"
                  :row-index="index"
                  :student="student"
                  :sorted-by="preferences.sortBy"
                  :class="{'list-group-item-info' : anchor === `#${student.uid}`}"
                  list-type="cohort"
                  class="list-group-item border-left-0 border-right-0" />
              </div>
              <div v-if="domain === 'admitted_students'" id="admitted-students-cohort-students" class="list-group mr-2">
                <SortableAdmits :admitted-students="students" />
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
      <div v-if="showHistory">
        <CohortHistory />
      </div>
    </div>
  </div>
</template>

<script>
import ApplyAndSaveButtons from '@/components/cohort/ApplyAndSaveButtons';
import CohortEditSession from '@/mixins/CohortEditSession';
import CohortHistory from '@/components/cohort/CohortHistory';
import CohortPageHeader from '@/components/cohort/CohortPageHeader';
import Context from '@/mixins/Context';
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import CurrentUserExtras from '@/mixins/CurrentUserExtras';
import FilterRow from '@/components/cohort/FilterRow';
import Loading from '@/mixins/Loading';
import Pagination from '@/components/util/Pagination';
import Scrollable from '@/mixins/Scrollable';
import SectionSpinner from '@/components/util/SectionSpinner';
import SortableAdmits from '@/components/admit/SortableAdmits';
import SortBy from '@/components/student/SortBy';
import Spinner from '@/components/util/Spinner';
import StudentRow from '@/components/student/StudentRow';
import Util from '@/mixins/Util';

export default {
  name: 'Cohort',
  components: {
    ApplyAndSaveButtons,
    CohortHistory,
    CohortPageHeader,
    CuratedGroupSelector,
    FilterRow,
    Pagination,
    SectionSpinner,
    SortableAdmits,
    SortBy,
    Spinner,
    StudentRow
  },
  mixins: [
    CohortEditSession,
    Context,
    Loading,
    Scrollable,
    CurrentUserExtras,
    Util
  ],
  data: () => ({
    pageNumber: undefined,
    showFilters: undefined,
    showHistory: false
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
      this.loaded(this.cohortName);
    } else {
      const domain = this.$route.query.domain || 'default';
      const id = this.toInt(this.get(this.$route, 'params.id'));
      this.init({
        id,
        orderBy: this.preferences.sortBy,
        domain
      }).then(() => {
        this.showFilters = !this.isCompactView;
        this.pageNumber = this.pagination.currentPage;
        const pageTitle = this.cohortId ? this.cohortName : 'Create Cohort';
        this.setPageTitle(pageTitle);
        this.loaded(pageTitle);
        this.putFocusNextTick(
          this.cohortId ? 'cohort-name' : 'create-cohort-h1'
        );
        this.$ga.cohortEvent(this.cohortId || '', this.cohortName || '', 'view');
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
        const action = `Sort students by ${sortBy}`;
        this.alertScreenReader(action);
        this.$ga.cohortEvent(this.cohortId || '', this.cohortName || '', action);
      }
    });
  },
  methods: {
    filterRowUniqueKey: (filter, index) => `${filter.key}-${filter.value}-${index}`,
    goToPage(page) {
      if (page > 1) {
        const action = `Go to page ${page}`;
        this.alertScreenReader(action);
        this.$ga.cohortEvent(this.cohortId || '', this.cohortName || '', action);
      }
      this.setPagination(page);
      this.onPageNumberChange().then(this.scrollToTop);
    },
    setPagination(page) {
      this.pageNumber = page;
      this.setCurrentPage(this.pageNumber);
    },
    toggleShowHistory(value) {
      this.showHistory = value;
      if (value && !this.isCompactView) {
        this.toggleCompactView();
      }
      if (!value) {
        this.onPageNumberChange().then(this.scrollToTop);
      }
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
