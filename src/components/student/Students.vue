<template>
  <div class="cohort-column-results">
    <div class="cohort-list-header">
      <div class="cohort-list-header-column-01"></div>
      <div class="cohort-list-header-column-02">
        <div class="cohort-sort-column" v-if="students.length">
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
    <div v-if="!students.length && listType === 'curatedGroup'">
      This curated group has no students. Start adding students from their profile pages to your
      <strong>{{ listName }}</strong> group:
      <SearchStudents :withButton="true"/>
    </div>
    <div v-if="students.length">
      <div id="curated-cohort-students" class="list-group">
        <StudentRow :student="student"
                    :sort="sort"
                    :id="`student-${student.uid}`"
                    class="list-group-item student-list-item"
                    :class="{'list-group-item-info' : anchor === `#${student.uid}`}"
                    v-for="(student, index) in orderedStudents"
                    :key="index"/>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import Scrollable from '@/mixins/Scrollable';
import SearchStudents from '@/components/sidebar/SearchStudents';
import StudentRow from '@/components/student/StudentRow';
import UserMetadata from '@/mixins/UserMetadata';

export default {
  name: 'Students',
  props: {
    listName: String,
    listType: String,
    students: Array
  },
  components: {
    SearchStudents,
    StudentRow
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
    orderedStudents: function() {
      return this.students.slice(0).sort(this.$_Students_compareStudents);
    },
    anchor: () => location.hash
  },
  methods: {
    $_Students_levelComparator: function(level) {
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
    $_Students_compareNumbers: function(thisNumber, thatNumber) {
      return (thisNumber >= thatNumber) - (thisNumber <= thatNumber);
    },
    $_Students_compareStudents: function(thisStudent, thatStudent) {
      switch (this.sort.selected) {
        case 'first_name':
          return thisStudent.firstName.localeCompare(thatStudent.firstName);
        case 'last_name':
          return thisStudent.lastName.localeCompare(thatStudent.lastName);
        // group_name here refers to team groups (i.e., athletic memberships) and not the user-created cohorts you'd expect.
        case 'group_name':
          return _.get(
            thisStudent,
            'athleticsProfile.athletics[0].groupName'
          ).localeCompare(
            _.get(thatStudent, 'athleticsProfile.athletics[0].groupName')
          );
        case 'gpa':
          return this.$_Students_compareNumbers(
            thisStudent.cumulativeGPA,
            thatStudent.cumulativeGPA
          );
        case 'level':
          return this.$_Students_compareNumbers(
            this.$_Students_levelComparator(thisStudent.level),
            this.$_Students_levelComparator(thatStudent.level)
          );
        case 'major':
          return _.get(thisStudent, 'majors[0]').localeCompare(
            _.get(thatStudent, 'majors[0]')
          );
        case 'units':
          return this.$_Students_compareNumbers(
            thisStudent.cumulativeUnits,
            thatStudent.cumulativeUnits
          );
        default:
          return 0;
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
