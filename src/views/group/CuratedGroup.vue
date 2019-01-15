<template>
  <div class="pl-3 pt-3">
    <Spinner/>
    <CuratedGroupHeader v-if="!loading" :curatedGroup="curatedGroup"/>
    <hr class="filters-section-separator" v-if="!loading && !error && size(curatedGroup.students)"/>
    <div class="cohort-column-results" v-if="!loading">
      <div class="d-flex m-2" v-if="size(curatedGroup.students) > 1">
        <div class="cohort-list-header-column-01"></div>
        <div class="cohort-list-header-column-02">
          <SortBy/>
        </div>
      </div>
      <div v-if="!size(curatedGroup.students)">
        This curated group has no students. Start adding students from their profile pages to your
        <strong>{{ curatedGroup.name }}</strong> group:
        <SearchStudents class="ml-0 mt-3" :withButton="true"/>
      </div>
      <div v-if="size(curatedGroup.students)">
        <div id="curated-cohort-students" class="list-group">
          <StudentRow :student="student"
                      listType="curatedGroup"
                      :sortedBy="preferences.sortBy"
                      :id="`student-${student.uid}`"
                      class="list-group-item student-list-item"
                      :class="{'list-group-item-info' : anchor === `#${student.uid}`}"
                      v-for="student in curatedGroup.students"
                      :key="student.sid"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CuratedGroupHeader from '@/components/curated/CuratedGroupHeader';
import Loading from '@/mixins/Loading';
import Scrollable from '@/mixins/Scrollable';
import SearchStudents from '@/components/sidebar/SearchStudents';
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
  mixins: [Loading, Scrollable, UserMetadata, Util],
  props: ['id'],
  components: {
    CuratedGroupHeader,
    SearchStudents,
    SortBy,
    Spinner,
    StudentRow
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
  computed: {
    anchor: () => location.hash
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
  },
  watch: {
    preferences: {
      handler() {
        this.sortStudents();
      },
      deep: true
    }
  }
};
</script>

<style scoped>
.student-list-item {
  border-left: none;
  border-right: none;
  display: flex;
}
</style>
