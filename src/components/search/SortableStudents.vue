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
      thead-class="sortable-table-header text-nowrap"
    >
      <template v-slot:cell(curated)="row">
        <StudentCheckbox
          v-if="options.includeCuratedCheckbox"
          :domain="domain"
          :student="row.item"
        />
      </template>

      <template v-slot:cell(avatar)="row">
        <StudentAvatar :key="row.item.sid" size="small" :student="row.item" />
        <div v-if="options.includeCuratedCheckbox" class="sr-only">
          <ManageStudent domain="default" :is-button-variant-link="true" :student="row.item" />
        </div>
      </template>

      <template v-slot:cell(lastName)="row">
        <span class="sr-only">Student name</span>
        <router-link
          v-if="row.item.uid"
          :id="`link-to-student-${row.item.uid}`"
          :class="{'demo-mode-blur': $currentUser.inDemoMode}"
          :to="studentRoutePath(row.item.uid, $currentUser.inDemoMode)"
          v-html="lastNameFirst(row.item)"
        />
        <span
          v-if="!row.item.uid"
          :id="`student-${row.item.sid}-has-no-uid`"
          class="font-weight-500"
          :class="{'demo-mode-blur': $currentUser.inDemoMode}"
          v-html="lastNameFirst(row.item)"
        />
        <span
          v-if="row.item.academicCareerStatus === 'Inactive' || displayAsAscInactive(row.item) || displayAsCoeInactive(row.item)"
          class="inactive-info-icon sortable-students-icon"
          uib-tooltip="Inactive"
          aria-label="Inactive"
          tooltip-placement="bottom"
        >
          <font-awesome icon="info-circle" />
        </span>
        <span
          v-if="row.item.academicCareerStatus === 'Completed'"
          class="sortable-students-icon"
          uib-tooltip="Graduated"
          aria-label="Graduated"
          tooltip-placement="bottom"
        >
          <font-awesome icon="graduation-cap" />
        </span>
      </template>

      <template v-slot:cell(sid)="row">
        <span class="sr-only">S I D </span>
        <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ row.item.sid }}</span>
      </template>

      <template v-if="!options.compact" v-slot:cell(majors[0])="row">
        <span class="sr-only">Major</span>
        <div v-if="!row.item.majors || row.item.majors.length === 0">--<span class="sr-only">No data</span></div>
        <div
          v-for="major in row.item.majors"
          :key="major"
        >
          {{ major }}
        </div>
      </template>

      <template v-if="!options.compact" v-slot:cell(expectedGraduationTerm.id)="row">
        <span class="sr-only">Expected graduation term</span>
        <div v-if="!row.item.expectedGraduationTerm">--<span class="sr-only">No data</span></div>
        <span class="text-nowrap">{{ abbreviateTermName(row.item.expectedGraduationTerm && row.item.expectedGraduationTerm.name) }}</span>
      </template>

      <template v-if="!options.compact" v-slot:cell(term.enrolledUnits)="row">
        <span class="sr-only">Term units</span>
        <div>{{ $_.get(row.item.term, 'enrolledUnits', 0) }}</div>
      </template>

      <template v-if="!options.compact" v-slot:cell(cumulativeUnits)="row">
        <span class="sr-only">Units completed</span>
        <div v-if="!row.item.cumulativeUnits">--<span class="sr-only">No data</span></div>
        <div v-if="row.item.cumulativeUnits">{{ numFormat(row.item.cumulativeUnits, '0.00') }}</div>
      </template>

      <template v-if="!options.compact" v-slot:cell(cumulativeGPA)="row">
        <span class="sr-only">GPA</span>
        <div v-if="$_.isNil(row.item.cumulativeGPA)">--<span class="sr-only">No data</span></div>
        <div v-if="!$_.isNil(row.item.cumulativeGPA)">{{ round(row.item.cumulativeGPA, 3) }}</div>
      </template>

      <template v-slot:cell(alertCount)="row">
        <span class="sr-only">Issue count</span>
        <div class="float-right mr-2">
          <div
            v-if="!row.item.alertCount"
            :aria-label="`No alerts for ${row.item.name}`"
            class="bg-white border pl-3 pr-3 rounded-pill text-muted"
          >
            0
          </div>
          <div
            v-if="row.item.alertCount"
            :aria-label="`${row.item.alertCount} alerts for ${row.item.name}`"
            class="bg-white border border-warning font-weight-bolder pill-alerts-per-student pl-3 pr-3 rounded-pill"
          >
            {{ row.item.alertCount }}
          </div>
        </div>
      </template>
    </b-table>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import StudentAvatar from '@/components/student/StudentAvatar'
import StudentCheckbox from '@/components/curated/dropdown/StudentCheckbox'
import StudentMetadata from '@/mixins/StudentMetadata'
import Util from '@/mixins/Util'

export default {
  name: 'SortableStudents',
  components: {
    ManageStudent,
    StudentAvatar,
    StudentCheckbox
  },
  mixins: [Context, StudentMetadata, Util],
  props: {
    domain: {
      required: true,
      type: String
    },
    options: {
      type: Object,
      default: () => ({
        compact: false,
        includeCuratedCheckbox: false,
        reverse: false,
        sortBy: 'lastName'
      })
    },
    students: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    fields: undefined,
    sortBy: undefined,
    sortDescending: undefined
  }),
  watch: {
    sortBy() {
      this.onChangeSortBy()
    },
    sortDescending() {
      this.onChangeSortBy()
    }
  },
  created() {
    this.sortBy = this.options.sortBy
    this.sortDescending = this.options.reverse

    const sortable = this.students.length > 1
    this.fields = [
      {key: 'curated', label: ''},
      {key: 'avatar', label: '', class: 'pr-0'},
      {key: 'lastName', label: 'Name', sortable},
      {key: 'sid', label: 'SID', sortable}
    ]
    if (this.options.compact) {
      this.fields = this.fields.concat([
        {key: 'alertCount', label: 'Alerts', sortable, class: 'alert-count text-right'}
      ])
    } else {
      this.fields = this.fields.concat([
        {key: 'majors[0]', label: 'Major', sortable, class: 'truncate-with-ellipsis'},
        {key: 'expectedGraduationTerm.id', label: 'Grad', sortable},
        {key: 'term.enrolledUnits', label: 'Term units', sortable},
        {key: 'cumulativeUnits', label: 'Units completed', sortable},
        {key: 'cumulativeGPA', label: 'GPA', sortable},
        {key: 'alertCount', label: 'Alerts', sortable, class: 'alert-count text-right'}
      ])
    }
  },
  methods: {
    abbreviateTermName: termName =>
      termName &&
      termName
        .replace('20', ' \'')
        .replace('Spring', 'Spr')
        .replace('Summer', 'Sum'),
    normalizeForSort(value) {
      return this.$_.isString(value) ? value.toLowerCase() : value
    },
    onChangeSortBy() {
      const field = this.$_.find(this.fields, ['key', this.sortBy])
      this.$announcer.polite(`Sorted by ${field.label}${this.sortDescending ? ', descending' : ''}`)
    },
    sortCompare(a, b, sortBy, sortDesc) {
      let aValue = this.$_.get(a, sortBy)
      let bValue = this.$_.get(b, sortBy)
      // If column type is number then nil is treated as zero.
      aValue = this.$_.isNil(aValue) && this.$_.isNumber(bValue) ? 0 : this.normalizeForSort(aValue)
      bValue = this.$_.isNil(bValue) && this.$_.isNumber(aValue) ? 0 : this.normalizeForSort(bValue)
      let result = this.sortComparator(aValue, bValue)
      if (result === 0) {
        this.$_.each(['lastName', 'firstName', 'sid'], field => {
          result = this.sortComparator(
            this.normalizeForSort(this.$_.get(a, field)),
            this.normalizeForSort(this.$_.get(b, field))
          )
          // Secondary sort is always ascending
          result *= sortDesc ? -1 : 1
          // Break from loop if comparator result is non-zero
          return result === 0
        })
      }
      return result
    }
  }
}
</script>

<style>
th.alert-count {
  padding-right: 15px;
}
.sortable-students-icon {
  margin-left: 5px;
}
</style>
