<template>
  <div class="m-3">
    <Spinner />
    <div v-if="!loading">
      <CuratedGroupHeader />
      <div v-show="mode !== 'bulkAdd'">
        <hr v-if="!error && totalStudentCount" class="filters-section-separator" />
        <div class="cohort-column-results">
          <div v-if="totalStudentCount > 1" class="d-flex m-2">
            <div class="cohort-list-header-column-01"></div>
            <div class="cohort-list-header-column-02">
              <SortBy v-if="totalStudentCount > 1" />
            </div>
          </div>
          <div v-if="size(students)">
            <div id="curated-cohort-students" class="list-group">
              <StudentRow
                v-for="(student, index) in students"
                :id="`student-${student.uid}`"
                :key="student.sid"
                :remove-student="removeStudent"
                :row-index="index"
                :student="student"
                :list-type="ownerId === user.id ? 'curatedGroupForOwner' : 'curatedGroup'"
                :sorted-by="preferences.sortBy"
                class="list-group-item student-list-item"
                :class="{'list-group-item-info' : anchor === `#${student.uid}`}" />
            </div>
            <div v-if="totalStudentCount > itemsPerPage" class="p-3">
              <Pagination
                :click-handler="onClickPagination"
                :init-page-number="pageNumber"
                :limit="10"
                :per-page="itemsPerPage"
                :total-rows="totalStudentCount" />
            </div>
          </div>
        </div>
      </div>
      <div v-if="!loading && mode === 'bulkAdd'">
        <h2 class="page-section-header-sub">Add Students</h2>
        <div class="w-75">
          Type or paste a list of Student Identification (SID) numbers below. Example: 9999999990, 9999999991
        </div>
        <CuratedGroupBulkAdd :bulk-add-sids="bulkAddSids" :curated-group-id="curatedGroupId" />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import CuratedGroupBulkAdd from '@/components/curated/CuratedGroupBulkAdd.vue';
import CuratedEditSession from '@/mixins/CuratedEditSession';
import CuratedGroupHeader from '@/components/curated/CuratedGroupHeader';
import Loading from '@/mixins/Loading';
import Pagination from '@/components/util/Pagination';
import Scrollable from '@/mixins/Scrollable';
import SortBy from '@/components/student/SortBy';
import Spinner from '@/components/util/Spinner';
import StudentRow from '@/components/student/StudentRow';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'CuratedGroup',
  components: {
    CuratedGroupBulkAdd,
    CuratedGroupHeader,
    Pagination,
    SortBy,
    Spinner,
    StudentRow
  },
  mixins: [Context, CuratedEditSession, Loading, Scrollable, UserMetadata, Util],
  props: {
    id: {
      required: true,
      type: [String, Number]
    }
  },
  data: () => ({
    error: undefined
  }),
  computed: {
    anchor: () => location.hash
  },
  created() {
    this.setUserPreference({key: 'sortBy', value: 'last_name'});
    this.init(parseInt(this.id)).then(group => {
      if (group) {
        this.loaded();
        this.setPageTitle(this.curatedGroupName);
        this.putFocusNextTick('curated-group-name');
        if (this.pageNumber > 1) {
          this.screenReaderAlert = `Go to page ${this.pageNumber}`;
          this.gaCuratedEvent({
            id: this.curatedGroupId,
            name: this.curatedGroupName,
            action: this.screenReaderAlert
          });
        }
      } else {
        this.$router.push({ path: '/404' });
      }
    });
    this.$eventHub.$on('sortBy-user-preference-change', sortBy => {
      if (!this.loading) {
        this.loadingStart();
        this.goToPage(1).then(() => {
          this.loaded();
          this.screenReaderAlert = `Students sorted by ${sortBy}`;
          this.gaCuratedEvent({
            id: this.curatedGroupId,
            name: this.curatedGroupName,
            action: this.screenReaderAlert
          });
        });
      }
    });
  },
  mounted() {
    this.$nextTick(function() {
      if (!this.anchor) {
        return false;
      }
      let anchor = this.anchor.replace(/(#)([0-9])/g, function(a, m1, m2) {
        return `${m1}student-${m2}`;
      });
      this.scrollTo(anchor);
    });
  },
  methods: {
    bulkAddSids(sids) {
      this.setMode(undefined);
      if (this.size(sids)) {
        this.alertScreenReader(`Adding ${sids.length} students`);
        this.setUserPreference({key: 'sortBy', value: 'last_name'});
        this.loadingStart();
        this.addStudents(sids).then(() => {
          this.loaded();
          this.putFocusNextTick('curated-group-name');
          this.alertScreenReader(`${sids.length} students added to group '${this.name}'`);
          this.gaCuratedEvent({
            id: this.curatedGroupId,
            name: this.curatedGroupName,
            action: 'Update curated group with bulk-add SIDs'
          });
        });
      } else {
        this.alertScreenReader('Cancelled bulk add of students');
        this.putFocusNextTick('curated-group-name');
      }
    },
    onClickPagination(pageNumber) {
      this.loadingStart();
      this.goToPage(pageNumber).then(() => {
        this.loaded();
        this.screenReaderAlert = `Page ${pageNumber} of cohort ${this.curatedGroupName}`;
        this.gaCuratedEvent({
          id: this.curatedGroupId,
          name: this.curatedGroupName,
          action: this.screenReaderAlert
        });
      });
    }
  }
};
</script>

<style scoped>
h3 {
  color: #666;
  font-size: 18px;
}
.cohort-list-header-column-01 {
  flex: 0 0 52px;
}
.cohort-list-header-column-02 {
  margin-left: auto;
  white-space: nowrap;
}
.student-list-item {
  border-left: none;
  border-right: none;
  display: flex;
}
</style>
