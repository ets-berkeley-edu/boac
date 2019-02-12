<template>
  <div>
    <div class="sr-only"
         role="alert"
         v-if="students && students.length && resorted">{{ currentSortDescription }}</div>
    <table class="table-full-width" v-if="students">
      <thead>
        <tr>
          <th class="group-summary-column group-summary-column-checkbox group-summary-column-header"
              v-if="options.includeCuratedCheckbox"></th>
          <th class="group-summary-column group-summary-column-photo group-summary-column-header"></th>
          <th class="group-summary-column group-summary-column-name group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'lastName')"
              role="button"
              :aria-label="sortOptions.lastName">
            Name
            <span v-if="options.sortBy === 'lastName'">
              <i :class="{
               'fas fa-caret-down': options.reverse,
               'fas fa-caret-up': !options.reverse
              }"></i>
            </span>
          </th>
          <th class="group-summary-column group-summary-column-sid group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'sid')"
              role="button"
              :aria-label="sortOptions.sid">
            SID
            <span v-if="options.sortBy === 'sid'">
              <i :class="{
               'fas fa-caret-down': options.reverse,
               'fas fa-caret-up': !options.reverse
              }"></i>
            </span>
          </th>
          <th class="group-summary-column group-summary-column-major group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'majors[0]')"
              role="button"
              :aria-label="sortOptions['majors[0]']">
            Major
            <span v-if="options.sortBy === 'majors[0]'">
              <i :class="{
               'fas fa-caret-down': options.reverse,
               'fas fa-caret-up': !options.reverse
              }"></i>
            </span>
          </th>
          <th class="group-summary-column group-summary-column-grad group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'expectedGraduationTerm.id')"
              role="button"
              :aria-label="sortOptions['expectedGraduationTerm.id']">
            Grad
            <span v-if="options.sortBy === 'expectedGraduationTerm.id'">
              <i :class="{
               'fas fa-caret-down': options.reverse,
               'fas fa-caret-up': !options.reverse
              }"></i>
            </span>
          </th>
          <th class="group-summary-column group-summary-column-units-term group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'term.enrolledUnits')"
              role="button"
              :aria-label="sortOptions['term.enrolledUnits']">
            Term Units
            <span v-if="options.sortBy === 'term.enrolledUnits'">
              <i :class="{
               'fas fa-caret-down': options.reverse,
               'fas fa-caret-up': !options.reverse
              }"></i>
            </span>
          </th>
          <th class="group-summary-column group-summary-column-units-completed group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'cumulativeUnits')"
              role="button"
              :aria-label="sortOptions.cumulativeUnits">
            Units Completed
            <span v-if="options.sortBy === 'cumulativeUnits'">
              <i :class="{
               'fas fa-caret-down': options.reverse,
               'fas fa-caret-up': !options.reverse
              }"></i>
            </span>
          </th>
          <th class="group-summary-column group-summary-column-gpa group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'cumulativeGPA')"
              role="button"
              :aria-label="sortOptions.cumulativeGPA">
            GPA
            <span class="caret" v-if="options.sortBy === 'cumulativeGPA'">
              <i :class="{
               'fas fa-caret-down': options.reverse,
               'fas fa-caret-up': !options.reverse
              }"></i>
            </span>
          </th>
          <th class="group-summary-column group-summary-column-issues group-summary-column-header group-summary-header-sortable"
              v-on:click="sort(options, 'alertCount')"
              role="button"
              :aria-label="sortOptions.alertCount">
            Issues
            <span v-if="options.sortBy === 'alertCount'">
              <i :class="{
               'fas fa-caret-down': options.reverse,
               'fas fa-caret-up': !options.reverse
              }"></i>
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in sortedStudents" :key="student.sid">
          <td class="group-summary-column group-summary-column-checkbox"
              v-if="options.includeCuratedCheckbox">
            <div class="add-to-cohort-checkbox">
              <CuratedStudentCheckbox :sid="student.sid"/>
            </div>
          </td>
          <td class="group-summary-column group-summary-column-photo">
            <StudentAvatar :student="student" size="small"/>
          </td>
          <td class="group-summary-column group-summary-column-name">
            <span class="sr-only">{{ srText.lastName }}</span>
            <router-link :aria-label="'Go to profile page of ' + student.firstName + ' ' + student.lastName"
                         :class="{'demo-mode-blur': user.inDemoMode}"
                         :to="'/student/' + student.uid">{{ `${student.lastName}, ${student.firstName}` }}</router-link>
            <span class="home-inactive-info-icon"
                  uib-tooltip="Inactive"
                  tooltip-placement="bottom"
                  v-if="displayAsInactive(student)">
              <i class="fas fa-info-circle"></i>
            </span>
          </td>
          <td class="group-summary-column group-summary-column-sid">
            <span class="sr-only">{{ srText.sid }}</span>
            <span :class="{'demo-mode-blur': user.inDemoMode}">{{ student.sid }}</span>
          </td>
          <td class="group-summary-column group-summary-column-major">
            <span class="sr-only">{{ srText['majors[0]'] }}</span>
            <div v-if="student.majors.length === 0">--<span class="sr-only">No data</span></div>
            <div v-for="major in student.majors"
                 :key="major">{{ major }}</div>
          </td>
          <td class="group-summary-column group-summary-column-grad">
            <span class="sr-only">{{ srText['expectedGraduationTerm.id'] }}</span>
            <div v-if="!student.expectedGraduationTerm">--<span class="sr-only">No data</span></div>
            <span>{{ abbreviateTermName(student.expectedGraduationTerm && student.expectedGraduationTerm.name) }}</span>
          </td>
          <td class="group-summary-column group-summary-column-units-term">
            <span class="sr-only">{{ srText['term.enrolledUnits'] }}</span>
            <div>{{ get(student.term, 'enrolledUnits', 0) }}</div>
          </td>
          <td class="group-summary-column group-summary-column-units-completed">
            <span class="sr-only">{{ srText.cumulativeUnits }}</span>
            <div v-if="!student.cumulativeUnits">--<span class="sr-only">No data</span></div>
            <div v-if="student.cumulativeUnits">{{ student.cumulativeUnits | numFormat('0.00') }}</div>
          </td>
          <td class="group-summary-column group-summary-column-gpa">
            <span class="sr-only">{{ srText.cumulativeGPA }}</span>
            <div v-if="isNil(student.cumulativeGPA)">--<span class="sr-only">No data</span></div>
            <div v-if="!isNil(student.cumulativeGPA)">{{ student.cumulativeGPA | round(3) }}</div>
          </td>
          <td class="group-summary-column group-summary-column-issues">
            <span class="sr-only">{{ srText.alertCount }}</span>
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
import Context from '@/mixins/Context';
import CuratedStudentCheckbox from '@/components/curated/CuratedStudentCheckbox';
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentMetadata from '@/mixins/StudentMetadata';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

let SUPPLEMENTAL_SORT_BY = {
  lastName: 'asc',
  firstName: 'asc',
  sid: 'asc'
};

export default {
  name: 'SortableStudents',
  components: {
    CuratedStudentCheckbox,
    StudentAvatar
  },
  mixins: [Context, StudentMetadata, UserMetadata, Util],
  props: {
    students: Array,
    options: {
      type: Object,
      default: () => ({
        sortBy: 'lastName',
        includeCuratedCheckbox: false,
        reverse: false
      })
    }
  },
  data: () => ({
    currentSortDescription: null,
    srText: {
      lastName: 'student name',
      sid: 'S I D',
      'majors[0]': 'major',
      'expectedGraduationTerm.id': 'expected graduation term',
      'term.enrolledUnits': 'term units',
      cumulativeUnits: 'units completed',
      cumulativeGPA: 'GPA',
      alertCount: 'issue count'
    },
    resorted: false,
    sortOptions: {
      alertCount: null,
      cumulativeGPA: null,
      cumulativeUnits: null,
      sid: null,
      lastName: null
    }
  }),
  created() {
    this.setSortDescriptions();
  },
  computed: {
    sortedStudents() {
      return _.orderBy(
        this.students,
        this.iteratees(),
        _.concat(
          this.options.reverse ? 'desc' : 'asc',
          _.values(SUPPLEMENTAL_SORT_BY)
        )
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
    iteratees: function() {
      let iteratees = _.concat(
        this.options.sortBy,
        _.keys(SUPPLEMENTAL_SORT_BY)
      );
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
      this.sortOptions = {};
      this.currentSortDescription =
        'Sorted by ' + this.srText[this.options.sortBy];
      if (this.reverse) {
        this.currentSortDescription += ' descending';
      }
      const sortBy = this.sortBy;
      const reverse = this.reverse;
      this.sortOptions = _.mapValues(this.srText, function(value, key) {
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

<style>
.group-summary-column-header {
  color: #999;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
  vertical-align: top;
}
.group-summary-header-sortable {
  cursor: pointer;
}
</style>

<style scoped>
.group-summary-column {
  padding: 0 5px 0 8px;
}
.group-summary-column-checkbox {
  padding: 0;
  text-align: left;
  width: 40px;
}
.group-summary-column-gpa {
  text-align: right;
  width: 8%;
}
.group-summary-column-grad {
  text-align: left;
  white-space: nowrap;
  width: 8%;
}
.group-summary-column-issues {
  text-align: center;
  width: 10%;
}
.group-summary-column-major {
  width: 20%;
}
.group-summary-column-major div {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.group-summary-column-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 20%;
}
.group-summary-column-photo {
  width: 40px;
}
.group-summary-column-sid {
  overflow: hidden;
  text-overflow: ellipsis;
  width: 15%;
}
.group-summary-column-units-completed {
  line-height: 1.4em;
  overflow-wrap: normal;
  text-align: right;
  width: 10%;
}
.group-summary-column-units-term {
  line-height: 1.4em;
  overflow-wrap: normal;
  text-align: right;
  width: 5%;
}
.group-summary-header-issues {
  width: 10%;
}
</style>
