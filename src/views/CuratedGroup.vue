<template>
  <div class="pl-3 pt-3">
    <Spinner />
    <div v-if="!loading">
      <CuratedGroupHeader :curated-group="curatedGroup" :mode="mode" :set-mode="setMode" />
      <div v-if="mode !== 'bulkAdd'">
        <hr v-if="!error && size(curatedGroup.students)" class="filters-section-separator" />
        <div class="cohort-column-results">
          <div v-if="size(curatedGroup.students) > 1" class="d-flex m-2">
            <div class="cohort-list-header-column-01"></div>
            <div class="cohort-list-header-column-02">
              <SortBy />
            </div>
          </div>
          <div v-if="!size(curatedGroup.students)">
            This curated group has no students. Start adding students from their profile pages to your
            <strong>{{ curatedGroup.name }}</strong> group:
            <SearchForm class="ml-0 mt-3" :domain="['students']" context="pageBody" />
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
          </div>
        </div>
      </div>
      <div v-if="mode === 'bulkAdd'">
        <h2 class="page-section-header-sub">Bulk Add Students</h2>
        <div>
          Add to your curated group of students <strong>{{ curatedGroup.name }}</strong> by adding
          Student Identification (SID) numbers below.
        </div>
        <h3 class="page-section-header-sub mt-3">Add SID numbers</h3>
        <div>
          Type or paste a list of SID numbers. Example: 9999999990, 9999999991
        </div>
        <CuratedGroupBulkAdd :bulk-add-sids="bulkAddSids" :curated-group-id="curatedGroup.id" />
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
import Scrollable from '@/mixins/Scrollable';
import SearchForm from '@/components/sidebar/SearchForm';
import SortBy from '@/components/student/SortBy';
import Spinner from '@/components/util/Spinner';
import store from '@/store';
import StudentRow from '@/components/student/StudentRow';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { addStudents, getCuratedGroup, removeFromCuratedGroup } from '@/api/curated';

let SUPPLEMENTAL_SORT_BY = ['lastName', 'firstName', 'sid'];

export default {
  name: 'CuratedGroup',
  components: {
    CuratedGroupBulkAdd,
    CuratedGroupHeader,
    SearchForm,
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
    mode: undefined,
    sortByMappings: {
      first_name: 'firstName',
      gpa: 'cumulativeGPA',
      group_name: 'athleticsProfile.athletics[0].groupName',
      last_name: 'lastName',
      level: 'sortableLevel',
      major: 'majors[0]',
      units: 'cumulativeUnits'
    }
  }),
  computed: {
    anchor: () => location.hash
  },
  created() {
    store.dispatch('user/setUserPreference', {
      key: 'sortBy',
      value: 'last_name'
    });
    getCuratedGroup(this.id).then(data => {
      if (data) {
        this.curatedGroup = data;
        this.setPageTitle(this.curatedGroup.name);
        this.sortStudents();
        this.loaded();
        this.putFocusNextTick('curated-group-name');
      } else {
        this.$router.push({ path: '/404' });
      }
    });
    this.$eventHub.$on('curated-group-remove-student', sid =>
      this.$_Students_removeStudent(sid)
    );
    this.$eventHub.$on('sort-by-changed-by-user', () => this.sortStudents());
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
        const done = () => {
          this.gaCuratedEvent(
            this.curatedGroup.id,
            this.curatedGroup.name,
            'Update curated group with bulk-add SIDs'
          );
          this.alertScreenReader(`${sids.length} students added to group '${this.curatedGroup.name}'`);
          this.putFocusNextTick('curated-group-name');
          this.mode = undefined;
        };
        addStudents(this.curatedGroup, sids)
          .then(group => {
            this.curatedGroup = group
          })
          .finally(() => setTimeout(done, 2000));
      } else {
        this.mode = undefined;
        this.alertScreenReader('Cancelled bulk add of students');
        this.putFocusNextTick('curated-group-name');
      }
    },
    sortStudents() {
      this.each(this.curatedGroup.students, student =>
        this.setSortableLevel(student)
      );
      this.curatedGroup.students = this.orderBy(
        this.curatedGroup.students,
        this.iteratees()
      );
    },
    iteratees() {
      let iteratees = this.concat(
        this.sortByMappings[this.preferences.sortBy],
        SUPPLEMENTAL_SORT_BY
      );
      return this.map(iteratees, iter => {
        return student => {
          let sortVal = this.get(student, iter);
          if (typeof sortVal === 'string') {
            sortVal = sortVal.toLowerCase();
          }
          return sortVal;
        };
      });
    },
    setMode(mode) {
      this.mode = mode;
    },
    setSortableLevel(student) {
      switch (student.level) {
        case 'Freshman':
          student.sortableLevel = 1;
          break;
        case 'Sophomore':
          student.sortableLevel = 2;
          break;
        case 'Junior':
          student.sortableLevel = 3;
          break;
        case 'Senior':
          student.sortableLevel = 4;
          break;
        default:
          student.sortableLevel = 0;
          break;
      }
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
