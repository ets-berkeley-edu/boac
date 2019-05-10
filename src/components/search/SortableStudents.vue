<template>
  <div>
    <table v-if="students" class="table-full-width">
      <thead>
        <tr>
          <th
            v-if="options.includeCuratedCheckbox"
            class="column column-checkbox sortable-table-header"></th>
          <th class="column column-photo sortable-table-header"></th>
          <th
            class="column column-name sortable-table-header cursor-pointer"
            role="button"
            :aria-label="sortOptions.lastName"
            @click="sort(options, 'lastName')">
            Name
            <span v-if="options.sortBy === 'lastName'">
              <i
                :class="{
                  'fas fa-caret-down': options.reverse,
                  'fas fa-caret-up': !options.reverse
                }"></i>
            </span>
          </th>
          <th
            class="column column-sid sortable-table-header cursor-pointer"
            role="button"
            :aria-label="sortOptions.sid"
            @click="sort(options, 'sid')">
            SID
            <span v-if="options.sortBy === 'sid'">
              <i
                :class="{
                  'fas fa-caret-down': options.reverse,
                  'fas fa-caret-up': !options.reverse
                }"></i>
            </span>
          </th>
          <th
            class="column column-major sortable-table-header cursor-pointer"
            role="button"
            :aria-label="sortOptions['majors[0]']"
            @click="sort(options, 'majors[0]')">
            Major
            <span v-if="options.sortBy === 'majors[0]'">
              <i
                :class="{
                  'fas fa-caret-down': options.reverse,
                  'fas fa-caret-up': !options.reverse
                }"></i>
            </span>
          </th>
          <th
            class="column column-grad sortable-table-header cursor-pointer"
            role="button"
            :aria-label="sortOptions['expectedGraduationTerm.id']"
            @click="sort(options, 'expectedGraduationTerm.id')">
            Grad
            <span v-if="options.sortBy === 'expectedGraduationTerm.id'">
              <i
                :class="{
                  'fas fa-caret-down': options.reverse,
                  'fas fa-caret-up': !options.reverse
                }"></i>
            </span>
          </th>
          <th
            class="column column-units-term sortable-table-header cursor-pointer"
            role="button"
            :aria-label="sortOptions['term.enrolledUnits']"
            @click="sort(options, 'term.enrolledUnits')">
            Term Units
            <span v-if="options.sortBy === 'term.enrolledUnits'">
              <i
                :class="{
                  'fas fa-caret-down': options.reverse,
                  'fas fa-caret-up': !options.reverse
                }"></i>
            </span>
          </th>
          <th
            class="column column-units-completed sortable-table-header cursor-pointer"
            role="button"
            :aria-label="sortOptions.cumulativeUnits"
            @click="sort(options, 'cumulativeUnits')">
            Units Completed
            <span v-if="options.sortBy === 'cumulativeUnits'">
              <i
                :class="{
                  'fas fa-caret-down': options.reverse,
                  'fas fa-caret-up': !options.reverse
                }"></i>
            </span>
          </th>
          <th
            class="column column-gpa sortable-table-header cursor-pointer"
            role="button"
            :aria-label="sortOptions.cumulativeGPA"
            @click="sort(options, 'cumulativeGPA')">
            GPA
            <span v-if="options.sortBy === 'cumulativeGPA'" class="caret">
              <i
                :class="{
                  'fas fa-caret-down': options.reverse,
                  'fas fa-caret-up': !options.reverse
                }"></i>
            </span>
          </th>
          <th
            class="column column-issues sortable-table-header cursor-pointer"
            role="button"
            :aria-label="sortOptions.alertCount"
            @click="sort(options, 'alertCount')">
            Issues
            <span v-if="options.sortBy === 'alertCount'">
              <i
                :class="{
                  'fas fa-caret-down': options.reverse,
                  'fas fa-caret-up': !options.reverse
                }"></i>
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in sortedStudents" :key="student.sid">
          <td
            v-if="options.includeCuratedCheckbox"
            class="column column-checkbox">
            <CuratedStudentCheckbox :student="student" />
          </td>
          <td class="column column-photo">
            <StudentAvatar :student="student" size="small" />
          </td>
          <td class="column column-name">
            <span class="sr-only">{{ srText.lastName }}</span>
            <router-link
              :aria-label="'Go to profile page of ' + student.firstName + ' ' + student.lastName"
              :class="{'demo-mode-blur': user.inDemoMode}"
              :to="'/student/' + student.uid">
              {{ `${student.lastName}, ${student.firstName}` }}
            </router-link>
            <span
              v-if="displayAsInactive(student)"
              class="home-inactive-info-icon"
              uib-tooltip="Inactive"
              tooltip-placement="bottom">
              <i class="fas fa-info-circle"></i>
            </span>
          </td>
          <td class="column column-sid">
            <span class="sr-only">{{ srText.sid }}</span>
            <span :class="{'demo-mode-blur': user.inDemoMode}">{{ student.sid }}</span>
          </td>
          <td class="column column-major">
            <span class="sr-only">{{ srText['majors[0]'] }}</span>
            <div v-if="student.majors.length === 0">--<span class="sr-only">No data</span></div>
            <div
              v-for="major in student.majors"
              :key="major">
              {{ major }}
            </div>
          </td>
          <td class="column column-grad">
            <span class="sr-only">{{ srText['expectedGraduationTerm.id'] }}</span>
            <div v-if="!student.expectedGraduationTerm">--<span class="sr-only">No data</span></div>
            <span>{{ abbreviateTermName(student.expectedGraduationTerm && student.expectedGraduationTerm.name) }}</span>
          </td>
          <td class="column column-units-term">
            <span class="sr-only">{{ srText['term.enrolledUnits'] }}</span>
            <div>{{ get(student.term, 'enrolledUnits', 0) }}</div>
          </td>
          <td class="column column-units-completed">
            <span class="sr-only">{{ srText.cumulativeUnits }}</span>
            <div v-if="!student.cumulativeUnits">--<span class="sr-only">No data</span></div>
            <div v-if="student.cumulativeUnits">{{ student.cumulativeUnits | numFormat('0.00') }}</div>
          </td>
          <td class="column column-gpa">
            <span class="sr-only">{{ srText.cumulativeGPA }}</span>
            <div v-if="isNil(student.cumulativeGPA)">--<span class="sr-only">No data</span></div>
            <div v-if="!isNil(student.cumulativeGPA)">{{ student.cumulativeGPA | round(3) }}</div>
          </td>
          <td class="column column-issues">
            <span class="sr-only">{{ srText.alertCount }}</span>
            <div
              v-if="!student.alertCount"
              class="home-issues-pill home-issues-pill-zero"
              :aria-label="'No alerts for ' + student.firstName + ' ' + student.lastName"
              tabindex="0">
              0
            </div>
            <div
              v-if="student.alertCount"
              class="home-issues-pill home-issues-pill-nonzero"
              :aria-label="student.alertCount + ' alerts for ' + student.firstName + ' ' + student.lastName"
              tabindex="0">
              {{ student.alertCount }}
            </div>
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
  created() {
    this.setSortDescriptions();
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
          } else if (_.isNil(sortVal)) {
            sortVal = 0;
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
      this.alertScreenReader(`Sorted by ${this.srText[this.options.sortBy]} ${this.options.reverse ? 'descending' : ''}`);
    },
    setSortDescriptions() {
      this.sortOptions = {};
      const sortBy = this.sortBy;
      const reverse = this.options.reverse;
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

<style scoped>
.column {
  padding: 0 5px 0 8px;
}
.column-checkbox {
  padding: 0;
  text-align: left;
  width: 20px;
}
.column-gpa {
  text-align: right;
  width: 8%;
}
.column-grad {
  text-align: left;
  white-space: nowrap;
  width: 8%;
}
.column-issues {
  text-align: center;
  width: 10%;
}
.column-major {
  width: 20%;
}
.column-major div {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.column-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 20%;
}
.column-photo {
  width: 40px;
}
.column-sid {
  overflow: hidden;
  text-overflow: ellipsis;
  width: 15%;
}
.column-units-completed {
  line-height: 1.4em;
  overflow-wrap: normal;
  text-align: right;
  width: 10%;
}
.column-units-term {
  line-height: 1.4em;
  overflow-wrap: normal;
  text-align: right;
  width: 5%;
}
</style>
