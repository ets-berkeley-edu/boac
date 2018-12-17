<template>
  <div class="cohort-column-results">
    <div class="cohort-list-header">
      <div class="cohort-list-header-column-01"></div>
      <div class="cohort-list-header-column-02">
        <div class="cohort-sort-column">
          <label class="cohort-sort-label" for="curated-cohort-sort-by">Sort by</label>
          <select id="curated-cohort-sort-by"
                  class="form-control"
                  v-model="sort.selected">
            <option v-for="o in sort.options"
                    :key="o.value"
                    :value="o.value">{{ o.name }}</option>
          </select>
        </div>
      </div>
    </div>
    <div v-if="!curatedGroup.students.length">
      This curated group has no students. Start adding students from their profile pages to your
      <strong>{{ curatedGroup.name }}</strong> group:
      <SearchStudents :withButton="true"/>
    </div>
    <div v-if="curatedGroup.students.length">
      <div id="curated-cohort-students" class="list-group">
        <CuratedGroupStudent :student="student"
                             :sort="sort"
                             :id="`student-${student.uid}`"
                             class="list-group-item student-list-item"
                             :class="{'list-group-item-info' : anchor === `#${student.uid}`}"
                             v-for="(student, index) in orderedStudents"
                             :key="index">
        </CuratedGroupStudent>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import { removeFromCuratedGroup } from '@/api/curated';
import store from '@/store';
import CuratedGroupStudent from '@/components/curated/CuratedGroupStudent.vue';
import Scrollable from '@/mixins/Scrollable';
import SearchStudents from '@/components/sidebar/SearchStudents.vue';
import UserMetadata from '@/mixins/UserMetadata';

export default {
  name: 'CuratedGroupList',
  props: {
    curatedGroup: Object
  },
  components: {
    SearchStudents,
    CuratedGroupStudent
  },
  mixins: [UserMetadata, Scrollable],
  data() {
    return {
      sort: {
        selected: 'last_name',
        options: []
      }
    };
  },
  created() {
    let options = [
      { name: 'First Name', value: 'first_name', available: true },
      { name: 'Last Name', value: 'last_name', available: true },
      { name: 'GPA', value: 'gpa', available: true },
      { name: 'Level', value: 'level', available: true },
      { name: 'Major', value: 'major', available: true },
      { name: 'Team', value: 'group_name', available: this.canViewAsc },
      { name: 'Units Completed', value: 'units', available: true }
    ];
    this.sort.options = _.filter(options, 'available');
    this.$eventHub.$on('curated-group-remove-student', sid =>
      this.$_CuratedGroupList_removeStudent(sid)
    );
  },
  mounted() {
    this.$nextTick(function() {
      let anchor = this.anchor.replace(/(#)([0-9])/g, function(a, m1, m2) {
        return `${m1}student-${m2}`;
      });
      this.scrollTo(anchor);
    });
  },
  computed: {
    orderedStudents: function() {
      return this.curatedGroup.students
        .slice(0)
        .sort(this.$_CuratedGroupList_studentComparator);
    },
    anchor: () => location.hash
  },
  methods: {
    $_CuratedGroupList_removeStudent: function(sid) {
      removeFromCuratedGroup(this.curatedGroup.id, sid).then(() => {
        let deleteIndex = this.curatedGroup.students.findIndex(student => {
          return student.sid === sid;
        });
        this.curatedGroup.students.splice(deleteIndex, 1);
        this.curatedGroup.studentCount = this.curatedGroup.students.length;
        store.commit('curated/updateCuratedGroup', this.curatedGroup);
      });
    },
    $_CuratedGroupList_levelComparator: function(level) {
      switch (level) {
        case 'Freshman':
          return 1;
        case 'Sophomore':
          return 2;
        case 'Junior':
          return 3;
        case 'Senior':
          return 4;
        default:
          return 0;
      }
    },
    $_CuratedGroupList_studentComparator: function(student) {
      switch (this.sort.selected) {
        case 'first_name':
          return student.firstName;
        case 'last_name':
          return student.lastName;
        // group_name here refers to team groups (i.e., athletic memberships) and not the user-created cohorts you'd expect.
        case 'group_name':
          return _.get(student, 'athleticsProfile.athletics[0].groupName');
        case 'gpa':
          return student.cumulativeGPA;
        case 'level':
          return this.$_CuratedGroupList_levelComparator(student.level);
        case 'major':
          return _.get(student, 'majors[0]');
        case 'units':
          return student.cumulativeUnits;
        default:
          return '';
      }
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
