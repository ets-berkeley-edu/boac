<template>
  <div class="m-3">
    <Spinner />
    <div v-if="!loading">
      <CuratedGroupHeader :curated-group="curatedGroup" :mode="mode" :set-mode="setMode" />
      <div v-show="mode !== 'bulkAdd'">
        <hr v-if="!error && size(curatedGroup.students)" class="filters-section-separator" />
        <div class="cohort-column-results">
          <div v-if="size(curatedGroup.students) > 1" class="d-flex m-2">
            <div class="cohort-list-header-column-01"></div>
            <div class="cohort-list-header-column-02">
              <SortBy v-if="curatedGroup.students.length > 1" />
            </div>
          </div>
          <div v-if="size(curatedGroup.students)">
            <div id="curated-cohort-students" class="list-group">
              <StudentRow
                v-for="(student, index) in curatedGroup.students"
                :id="`student-${student.uid}`"
                :key="student.sid"
                :row-index="index"
                :student="student"
                list-type="curatedGroup"
                :sorted-by="preferences.sortBy"
                class="list-group-item student-list-item"
                :class="{'list-group-item-info' : anchor === `#${student.uid}`}" />
            </div>
            <div v-if="curatedGroup.studentCount > itemsPerPage" class="p-3">
              <Pagination
                :click-handler="goToPage"
                :init-page-number="pageNumber"
                :limit="10"
                :per-page="itemsPerPage"
                :total-rows="curatedGroup.studentCount" />
            </div>
          </div>
        </div>
      </div>
      <div v-if="mode === 'bulkAdd'">
        <h2 class="page-section-header-sub">Add Students</h2>
        <div class="w-75">
          Type or paste a list of Student Identification (SID) numbers below. Example: 9999999990, 9999999991
        </div>
        <CuratedGroupBulkAdd
          :bulk-add-sids="bulkAddSids"
          :curated-group-id="curatedGroup.id"
          :is-saving="isAddingStudents" />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import CuratedGroupBulkAdd from '@/components/curated/CuratedGroupBulkAdd.vue'
import CuratedGroupHeader from '@/components/curated/CuratedGroupHeader';
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import Loading from '@/mixins/Loading';
import Pagination from '@/components/util/Pagination';
import Scrollable from '@/mixins/Scrollable';
import SortBy from '@/components/student/SortBy';
import Spinner from '@/components/util/Spinner';
import store from '@/store';
import StudentRow from '@/components/student/StudentRow';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { addStudents, getCuratedGroup, removeFromCuratedGroup } from '@/api/curated';

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
  mixins: [Context, GoogleAnalytics, Loading, Scrollable, UserMetadata, Util],
  props: {
    id: [String, Number]
  },
  data: () => ({
    curatedGroup: {},
    error: undefined,
    isAddingStudents: false,
    itemsPerPage: 50,
    pageNumber: undefined,
    mode: undefined
  }),
  computed: {
    anchor: () => location.hash
  },
  created() {
    store.dispatch('user/setUserPreference', {
      key: 'sortBy',
      value: 'last_name'
    });
    this.goToPage(1);
    this.$eventHub.$on('curated-group-remove-student', sid =>
      this.$_Students_removeStudent(sid)
    );
    this.$eventHub.$on('sort-by-changed-by-user', sortBy => {
      this.goToPage(1);
      this.screenReaderAlert = `Sort students by ${sortBy}`;
      this.gaCuratedEvent(this.curatedGroup.id, this.curatedGroup.name, this.screenReaderAlert);
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
      if (this.size(sids)) {
        this.isAddingStudents = true;
        this.alertScreenReader(`Adding ${sids.length} students`);
        addStudents(this.curatedGroup, sids, true)
          .then(group => {
            this.curatedGroup = group;
            this.mode = undefined;
            this.putFocusNextTick('curated-group-name');
            this.alertScreenReader(`${sids.length} students added to group '${this.curatedGroup.name}'`);
            this.isAddingStudents = false;
            this.gaCuratedEvent(this.curatedGroup.id, this.curatedGroup.name, 'Update curated group with bulk-add SIDs');
          });
      } else {
        this.mode = undefined;
        this.alertScreenReader('Cancelled bulk add of students');
        this.putFocusNextTick('curated-group-name');
      }
    },
    goToPage(page) {
      this.pageNumber = page;
      if (page > 1) {
        this.screenReaderAlert = `Go to page ${page}`;
        this.gaCuratedEvent(this.curatedGroup.id, this.curatedGroup.name, this.screenReaderAlert);
      }
      this.loadingStart();
      let offset = this.multiply(this.pageNumber - 1, this.itemsPerPage);
      getCuratedGroup(this.id, this.preferences.sortBy, offset, this.itemsPerPage).then(data => {
        if (data) {
          this.curatedGroup = data;
          this.setPageTitle(this.curatedGroup.name);
          this.loaded();
          this.putFocusNextTick('curated-group-name');
        } else {
          this.$router.push({ path: '/404' });
        }
      });
    },
    setMode(mode) {
      this.mode = mode;
    },
    $_Students_removeStudent(sid) {
      removeFromCuratedGroup(this.curatedGroup.id, sid).then(() => {
        let deleteIndex = this.curatedGroup.students.findIndex(student => {
          return student.sid === sid;
        });
        this.curatedGroup.students.splice(deleteIndex, 1);
        this.curatedGroup.studentCount = this.curatedGroup.students.length;
        store.commit('curated/updateCuratedGroup', this.curatedGroup);
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
