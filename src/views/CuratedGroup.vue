<template>
  <div class="pl-3 pt-3">
    <Spinner />
    <CuratedGroupHeader v-if="!loading" :curated-group="curatedGroup" />
    <hr v-if="!loading && !error && size(curatedGroup.students)" class="filters-section-separator" />
    <div v-if="!loading" class="cohort-column-results">
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
            v-for="student in curatedGroup.students"
            :id="`student-${student.uid}`"
            :key="student.sid"
            :student="student"
            list-type="curatedGroup"
            :sorted-by="preferences.sortBy"
            class="list-group-item student-list-item"
            :class="{'list-group-item-info' : anchor === `#${student.uid}`}" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CuratedGroupHeader from '@/components/curated/CuratedGroupHeader';
import Loading from '@/mixins/Loading';
import Scrollable from '@/mixins/Scrollable';
import SearchForm from '@/components/sidebar/SearchForm';
import SortBy from '@/components/student/SortBy';
import Spinner from '@/components/util/Spinner';
import store from '@/store';
import StudentRow from '@/components/student/StudentRow';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { getCuratedGroup, removeFromCuratedGroup } from '@/api/curated';

let SUPPLEMENTAL_SORT_BY = ['lastName', 'firstName', 'sid'];

export default {
  name: 'CuratedGroup',
  components: {
    CuratedGroupHeader,
    SearchForm,
    SortBy,
    Spinner,
    StudentRow
  },
  mixins: [Loading, Scrollable, UserMetadata, Util],
  props: {
    id: Number
  },
  data: () => ({
    curatedGroup: {},
    error: undefined,
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
    setSortableLevel: student => {
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
    $_Students_removeStudent: function(sid) {
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
