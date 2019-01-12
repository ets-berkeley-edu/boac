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
                    :listType="listType"
                    :sort="sort"
                    :id="`student-${student.uid}`"
                    class="list-group-item student-list-item"
                    :class="{'list-group-item-info' : anchor === `#${student.uid}`}"
                    v-for="(student, index) in sortedStudents"
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

let SUPPLEMENTAL_SORT_BY = ['lastName', 'firstName', 'sid'];

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
        selected: 'lastName',
        options: []
      }
    };
  },
  created() {
    let options = [
      { name: 'First Name', value: 'firstName', available: true },
      { name: 'Last Name', value: 'lastName', available: true },
      { name: 'GPA', value: 'cumulativeGPA', available: true },
      { name: 'Level', value: 'sortableLevel', available: true },
      { name: 'Major', value: 'majors[0]', available: true },
      {
        name: 'Team',
        value: 'athleticsProfile.athletics[0].groupName',
        available: this.canViewAsc
      },
      { name: 'Units Completed', value: 'cumulativeUnits', available: true }
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
    sortedStudents() {
      _.each(this.students, student => this.setSortableLevel(student));
      return _.orderBy(this.students, this.iteratees());
    },
    anchor: () => location.hash
  },
  methods: {
    iteratees: function() {
      let iteratees = _.concat(this.sort.selected, SUPPLEMENTAL_SORT_BY);
      return _.map(iteratees, iter => {
        return student => {
          let sortVal = _.get(student, iter);
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
