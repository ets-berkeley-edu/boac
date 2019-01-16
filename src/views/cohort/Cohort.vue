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
        <FilterRow />
        <ApplyAndSaveButtons />
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
              <span class="sr-only"><span id="total-student-count">{{ totalStudentCount / pagination.itemsPerPage | ceil }}</span>
                pages of search results</span>
              <b-pagination id="pagination-widget"
                            size="md"
                            :total-rows="totalStudentCount"
                            :limit="10"
                            v-model="pageNumber"
                            :per-page="pagination.itemsPerPage"
                            :hide-goto-end-buttons="true"
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
import ApplyAndSaveButtons from '@/components/cohort/ApplyAndSaveButtons';
import CohortEditSession from '@/mixins/CohortEditSession';
import CohortPageHeader from '@/components/cohort/CohortPageHeader';
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import FilterRow from '@/components/cohort/FilterRow';
import Loading from '@/mixins/Loading';
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
      this.loaded();
    } else {
      let id = this.get(this.$route, 'params.id');
      this.init({
        id,
        orderBy: this.preferences.sortBy
      }).then(() => {
        this.showFilters = !this.isCompactView;
        this.currentPage = this.pagination.currentPage;
        this.loaded();
        this.putFocusNextTick(
          this.cohortId ? 'cohort-name' : 'create-cohort-h1'
        );
      });
    }
  },
  methods: {
    compositeKey: filter => `${filter.key}${filter.value}`,
    nextPage(page) {
      this.pageNumber = page || this.pageNumber;
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
    },
    preferences: {
      handler() {
        this.nextPage(1);
      },
      deep: true
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
.student-list-item {
  border-left: none;
  border-right: none;
  display: flex;
}
</style>
