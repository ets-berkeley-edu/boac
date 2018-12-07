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
                             class="list-group-item student-list-item"
                             :class="{'list-group-item-info' : anchor === student.uid}"
                             v-for="(student, index) in orderedStudents"
                             :key="index">
        </CuratedGroupStudent>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import CuratedGroupStudent from '@/components/curated/CuratedGroupStudent.vue';
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
  mixins: [UserMetadata],
  data: () => ({
    sort: {
      selected: 'last_name',
      options: []
    }
  }),
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
  computed: {
    orderedStudents: () =>
      _.orderBy(this.curatedGroup.students, this.studentComparator),
    anchor: () => location.hash
  },
  methods: {
    levelComparator: function(level) {
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
    studentComparator: function(student) {
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
          return this.levelComparator(student.level);
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
