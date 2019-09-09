<template>
  <div>
    <b-table
      :borderless="true"
      :fields="fields"
      :items="students"
      :no-sort-reset="true"
      :small="true"
      :sort-by.sync="sortBy"
      :sort-compare="sortCompare"
      :sort-desc.sync="sortDescending"
      stacked="md"
      thead-class="sortable-table-header text-nowrap">
      <template v-if="options.includeCuratedCheckbox" slot="curated" slot-scope="row">
        <CuratedStudentCheckbox :student="row.item" />
      </template>

      <template slot="avatar" slot-scope="row">
        <StudentAvatar :key="row.item.sid" :student="row.item" size="small" />
      </template>

      <template slot="lastName" slot-scope="row">
        <span class="sr-only">Student name</span>
        <router-link
          :id="`link-to-student-${row.item.uid}`"
          :aria-label="'Go to profile page of ' + row.item.firstName + ' ' + row.item.lastName"
          class="text-nowrap"
          :class="{'demo-mode-blur': user.inDemoMode}"
          :to="studentRoutePath(row.item.uid, user.inDemoMode)"
          v-html="`${row.item.lastName}, ${row.item.firstName}`"></router-link>
        <span
          v-if="row.item.academicCareerStatus === 'Inactive' || displayAsAscInactive(row.item) || displayAsCoeInactive(row.item)"
          class="home-inactive-info-icon sortable-students-icon"
          uib-tooltip="Inactive"
          tooltip-placement="bottom">
          <font-awesome icon="info-circle" />
        </span>
        <span
          v-if="row.item.academicCareerStatus === 'Completed'"
          class="sortable-students-icon"
          uib-tooltip="Graduated"
          tooltip-placement="bottom">
          <font-awesome icon="graduation-cap" />
        </span>
      </template>

      <template slot="sid" slot-scope="row">
        <span class="sr-only">S I D</span>
        <span :class="{'demo-mode-blur': user.inDemoMode}">{{ row.item.sid }}</span>
      </template>

      <template slot="majors[0]" slot-scope="row">
        <span class="sr-only">Major</span>
        <div v-if="!row.item.majors || row.item.majors.length === 0">--<span class="sr-only">No data</span></div>
        <div
          v-for="major in row.item.majors"
          :key="major">
          {{ major }}
        </div>
      </template>

      <template slot="expectedGraduationTerm.id" slot-scope="row">
        <span class="sr-only">Expected graduation term</span>
        <div v-if="!row.item.expectedGraduationTerm">--<span class="sr-only">No data</span></div>
        <span class="text-nowrap">{{ abbreviateTermName(row.item.expectedGraduationTerm && row.item.expectedGraduationTerm.name) }}</span>
      </template>

      <template slot="term.enrolledUnits" slot-scope="row">
        <span class="sr-only">Term units</span>
        <div>{{ get(row.item.term, 'enrolledUnits', 0) }}</div>
      </template>

      <template slot="cumulativeUnits" slot-scope="row">
        <span class="sr-only">Units completed</span>
        <div v-if="!row.item.cumulativeUnits">--<span class="sr-only">No data</span></div>
        <div v-if="row.item.cumulativeUnits">{{ row.item.cumulativeUnits | numFormat('0.00') }}</div>
      </template>

      <template slot="cumulativeGPA" slot-scope="row">
        <span class="sr-only">GPA</span>
        <div v-if="isNil(row.item.cumulativeGPA)">--<span class="sr-only">No data</span></div>
        <div v-if="!isNil(row.item.cumulativeGPA)">{{ row.item.cumulativeGPA | round(3) }}</div>
      </template>

      <template slot="alertCount" slot-scope="row">
        <span class="sr-only">Issue count</span>
        <div
          v-if="!row.item.alertCount"
          class="home-issues-pill home-issues-pill-zero"
          :aria-label="'No alerts for ' + row.item.firstName + ' ' + row.item.lastName"
          tabindex="0">
          0
        </div>
        <div
          v-if="row.item.alertCount"
          class="home-issues-pill home-issues-pill-nonzero"
          :aria-label="row.item.alertCount + ' alerts for ' + row.item.firstName + ' ' + row.item.lastName"
          tabindex="0">
          {{ row.item.alertCount }}
        </div>
      </template>
    </b-table>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import CuratedStudentCheckbox from '@/components/curated/CuratedStudentCheckbox';
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentMetadata from '@/mixins/StudentMetadata';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

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
  data() {
    return {
      fields: undefined,
      sortBy: this.options.sortBy,
      sortDescending: this.options.reverse
    }
  },
  watch: {
    sortBy() {
      this.onChangeSortBy();
    },
    sortDescending() {
      this.onChangeSortBy();
    }
  },
  created() {
    this.fields = this.options.includeCuratedCheckbox ? [{ key: 'curated', label: '' }] : [];
    this.fields = this.fields.concat([
      {key: 'curated', label: ''},
      {key: 'avatar', label: ''},
      {key: 'lastName', label: 'Name', sortable: true},
      {key: 'sid', label: 'SID', sortable: true},
      {key: 'majors[0]', label: 'Major', sortable: true, class: 'truncate-with-ellipsis'},
      {key: 'expectedGraduationTerm.id', label: 'Grad', sortable: true},
      {key: 'term.enrolledUnits', label: 'Term units', sortable: true},
      {key: 'cumulativeUnits', label: 'Units completed', sortable: true},
      {key: 'cumulativeGPA', label: 'GPA', sortable: true},
      {key: 'alertCount', label: 'Issues', sortable: true, class: 'text-center'}
    ]);
  },
  methods: {
    abbreviateTermName: termName =>
      termName &&
      termName
        .replace('20', " '")
        .replace('Spring', 'Spr')
        .replace('Summer', 'Sum'),
    onChangeSortBy() {
      const field = this.find(this.fields, ['key', this.sortBy]);
      this.alertScreenReader(`Sorted by ${field.label}${this.sortDescending ? ', descending' : ''}`);
    },
    sortCompare(a, b, sortBy, sortDesc) {
      let aValue = this.get(a, sortBy);
      let bValue = this.get(b, sortBy);
      // If column type is number then nil is treated as zero.
      aValue = this.isNil(aValue) && this.isNumber(bValue) ? 0 : aValue;
      bValue = this.isNil(bValue) && this.isNumber(aValue) ? 0 : bValue;
      let result = this.sortComparator(aValue, bValue);
      if (result === 0) {
        this.each(['lastName', 'firstName', 'sid'], field => {
          result = this.sortComparator(this.get(a, field), this.get(b, field));
          // Secondary sort is always ascending
          result *= sortDesc ? -1 : 1;
          // Break from loop if comparator result is non-zero
          return result === 0;
        });
      }
      return result;
    }
   }
};
</script>

<style scoped>
.sortable-students-icon {
  margin-left: 5px;
}
</style>
