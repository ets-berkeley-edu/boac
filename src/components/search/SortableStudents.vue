<template>
  <div>
    <div class="sr-only"
         role="alert"
         v-if="students && students.length && resorted">{{ currentSortDescription }}</div>
    <table class="table-full-width" v-if="students">
      <thead>
        <tr>
          <th class="group-summary-column group-summary-column-checkbox group-summary-column-header"
              v-if="options.curatedCohort"></th>
          <th class="group-summary-column group-summary-column-photo group-summary-column-header"></th>
          <th class="group-summary-column group-summary-column-name group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'sortableName')"
              v-bind:class="{dropup: !options.reverse}"
              role="button"
              :aria-label="sortOptions.sortableName">
            Name
            <span class="caret" v-if="options.sortBy === 'sortableName'"></span>
          </th>
          <th class="group-summary-column group-summary-column-sid group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'sid')"
              v-bind:class="{dropup: !options.reverse}"
              role="button"
              :aria-label="sortOptions.sid">
            SID
            <span class="caret" v-if="options.sortBy === 'sid'"></span>
          </th>
          <th class="group-summary-column group-summary-column-major group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'majors[0]')"
              v-bind:class="{dropup: !options.reverse}"
              role="button"
              :aria-label="sortOptions['majors[0]']">
            Major
            <span class="caret" v-if="options.sortBy === 'majors[0]'"></span>
          </th>
          <th class="group-summary-column group-summary-column-grad group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'expectedGraduationTerm.id')"
              v-bind:class="{dropup: !options.reverse}"
              role="button"
              :aria-label="sortOptions['expectedGraduationTerm.id']">
            Grad
            <span class="caret" v-if="options.sortBy === 'expectedGraduationTerm.id'"></span>
          </th>
          <th class="group-summary-column group-summary-column-units-term group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'term.enrolledUnits')"
              v-bind:class="{dropup: !options.reverse}"
              role="button"
              :aria-label="sortOptions['term.enrolledUnits']">
            Term Units
            <span class="caret" v-if="options.sortBy === 'term.enrolledUnits'"></span>
          </th>
          <th class="group-summary-column group-summary-column-units-completed group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'cumulativeUnits')"
              v-bind:class="{dropup: !options.reverse}"
              role="button"
              :aria-label="sortOptions.cumulativeUnits">
            Units Completed
            <span class="caret" v-if="options.sortBy === 'cumulativeUnits'"></span>
          </th>
          <th class="group-summary-column group-summary-column-gpa group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'cumulativeGPA')"
              v-bind:class="{dropup: !options.reverse}"
              role="button"
              :aria-label="sortOptions.cumulativeGPA">
            GPA
            <span class="caret" v-if="options.sortBy === 'cumulativeGPA'"></span>
          </th>
          <th class="group-summary-column group-summary-column-issues group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'alertCount')"
              v-bind:class="{dropup: !options.reverse}"
              role="button"
              :aria-label="sortOptions.alertCount">
            Issues
            <span class="caret" v-if="options.sortBy === 'alertCount'"></span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in sortedStudents" v-bind:key="student.sid">
          <td class="group-summary-column group-summary-column-checkbox">
            <div class="add-to-cohort-checkbox">
              <CuratedStudentCheckbox :sid="student.sid"/>
            </div>
          </td>
          <td class="group-summary-column group-summary-column-photo">
            <StudentAvatar :student="student" size="small"/>
          </td>
          <td class="group-summary-column group-summary-column-name">
            <span class="sr-only">{{ options.srText.sortableName }}</span>
            <a :aria-label="'Go to profile page of ' + student.firstName + ' ' + student.lastName"
               v-bind:class="{'demo-mode-blur': inDemoMode}"
               :href="'/student_' + student.uid">{{ student.sortableName }}</a>
            <span class="home-inactive-info-icon"
                  uib-tooltip="Inactive"
                  tooltip-placement="bottom"
                  v-if="displayAsInactive(student)">
              <i class="fas fa-info-circle"></i>
            </span>
          </td>
          <td class="group-summary-column group-summary-column-sid">
            <span class="sr-only">{{ options.srText.sid }}</span>
            <span v-bind:class="{'demo-mode-blur': inDemoMode}">{{ student.sid }}</span>
          </td>
          <td class="group-summary-column group-summary-column-major">
            <span class="sr-only">{{ options.srText['majors[0]'] }}</span>
            <div v-if="student.majors.length === 0">--<span class="sr-only">No data</span></div>
            <div v-for="major in student.majors"
                 v-bind:key="major"
                 v-if="student.majors.length > 0">{{ major }}</div>
          </td>
          <td class="group-summary-column group-summary-column-grad">
            <span class="sr-only">{{ options.srText['expectedGraduationTerm.id'] }}</span>
            <div v-if="!student.expectedGraduationTerm">--<span class="sr-only">No data</span></div>
            <span>{{ abbreviateTermName(student.expectedGraduationTerm && student.expectedGraduationTerm.name) }}</span>
          </td>
          <td class="group-summary-column group-summary-column-units-term">
            <span class="sr-only">{{ options.srText['term.enrolledUnits'] }}</span>
            <div>{{ student.term.enrolledUnits || '0' }}</div>
          </td>
          <td class="group-summary-column group-summary-column-units-completed">
            <span class="sr-only">{{ options.srText.cumulativeUnits }}</span>
            <div v-if="!student.cumulativeUnits">--<span class="sr-only">No data</span></div>
            <div v-if="student.cumulativeUnits">{{ student.cumulativeUnits | variablePrecisionNumber(2, 3) }}</div>
          </td>
          <td class="group-summary-column group-summary-column-gpa">
            <span class="sr-only">{{ options.srText.cumulativeGPA }}</span>
            <div v-if="!student.cumulativeGPA">--<span class="sr-only">No data</span></div>
            <div v-if="student.cumulativeGPA">{{ student.cumulativeGPA | round(3) }}</div>
          </td>
          <td class="group-summary-column group-summary-column-issues">
            <span class="sr-only">{{ options.srText.alertCount }}</span>
            <div class="home-issues-pill home-issues-pill-zero"
                 :aria-label="'No alerts for ' + student.firstName + ' ' + student.lastName"
                 tabindex="0"
                 v-if="!student.alertCount">0</div>
            <div class="home-issues-pill home-issues-pill-nonzero"
                 :aria-label="student.alertCount + ' alerts for ' + student.firstName + ' ' + student.lastName"
                 tabindex="0"
                 v-if="student.alertCount">{{ student.alertCount }}</div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import _ from 'lodash';
import AppConfig from '@/mixins/AppConfig';
import CuratedStudentCheckbox from '@/components/curated/CuratedStudentCheckbox';
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentMetadata from '@/mixins/StudentMetadata';
import UserMetadata from '@/mixins/UserMetadata';

export default {
  name: 'SortableStudents',
  components: {
    CuratedStudentCheckbox,
    StudentAvatar
  },
  mixins: [AppConfig, StudentMetadata, UserMetadata],
  created() {
    this.setSortDescriptions();
  },
  props: {
    students: Array
  },
  data: () => ({
    currentSortDescription: null,
    options: {
      sortBy: null,
      curatedCohort: false,
      reverse: false,
      srText: {
        sortableName: 'student name',
        sid: 'S I D',
        'majors[0]': 'major',
        'expectedGraduationTerm.id': 'expected graduation term',
        'term.enrolledUnits': 'term units',
        cumulativeUnits: 'units completed',
        cumulativeGPA: 'GPA',
        alertCount: 'issue count'
      }
    },
    resorted: false,
    sortOptions: {
      alertCount: null,
      cumulativeGPA: null,
      cumulativeUnits: null,
      sid: null,
      sortableName: null
    }
  }),
  computed: {
    sortedStudents() {
      return _.orderBy(
        this.students,
        this.options.sortBy,
        this.options.reverse ? 'desc' : 'asc'
      );
    }
  },
  methods: {
    abbreviateTermName: termName =>
      termName &&
      termName
        .replace('20', " '")
        .replace('Spring', 'Spr')
        .replace('Summer', 'Sum'),
    sort(options, sortBy) {
      if (options.sortBy === sortBy) {
        options.reverse = !options.reverse;
      } else {
        options.sortBy = sortBy;
        options.reverse = false;
      }
      this.resorted = true;
      this.setSortDescriptions();
    },
    setSortDescriptions() {
      const sortBy = this.options.sortBy;
      const reverse = this.options.reverse;
      this.sortOptions = {};
      this.currentSortDescription = 'Sorted by ' + this.options.srText[sortBy];
      if (reverse) {
        this.currentSortDescription += ' descending';
      }
      this.sortOptions = _.mapValues(this.options.srText, function(value, key) {
        let optionText = 'Sort by ' + value;
        if (key === sortBy) {
          optionText += reverse ? ' ascending' : ' descending';
        }
        return optionText;
      });
    }
  }
};
</script>
