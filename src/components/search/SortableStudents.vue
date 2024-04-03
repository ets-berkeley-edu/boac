<template>
  <v-data-table-virtual
    v-resize="onResize"
    borderless
    :cell-props="{
      class: 'pl-0'
    }"
    density="compact"
    :header-props="{
      class: 'pl-0 text-no-wrap'
    }"
    :headers="headers"
    :items="students"
    no-sort-reset
    :sort-by="[sortBy]"
    :sort-compare="sortCompare"
    stacked="md"
  >
    <template #header.avatar="{column}">
      <span class="sr-only">{{ column.title }}</span>
    </template>

    <template #item.curated="{item}">
      <CuratedStudentCheckbox
        v-if="options.includeCuratedCheckbox"
        class="mb-2"
        :domain="domain"
        :student="item"
      />
    </template>

    <template #item.avatar="{item}">
      <StudentAvatar
        :key="item.sid"
        size="small"
        :student="item"
      />
      <div v-if="options.includeCuratedCheckbox" class="sr-only">
        <ManageStudent domain="default" :is-button-variant-link="true" :student="item" />
      </div>
    </template>

    <template #item.name="{item}">
      <div class="text-no-wrap">
        <span class="sr-only">Student name</span>
        <router-link
          v-if="item.uid"
          :id="`link-to-student-${item.uid}`"
          class="text-primary"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
          :to="studentRoutePath(item.uid, useContextStore().currentUser.inDemoMode)"
          v-html="lastNameFirst(item)"
        />
        <span
          v-if="!item.uid"
          :id="`student-${item.sid}-has-no-uid`"
          class="font-weight-500"
          :class="{'demo-mode-blur': useContextStore().currentUser.inDemoMode}"
          v-html="lastNameFirst(item)"
        />
        <span
          v-if="item.academicCareerStatus === 'Inactive' || displayAsAscInactive(item) || displayAsCoeInactive(item)"
          class="inactive-info-icon sortable-students-icon"
          uib-tooltip="Inactive"
          aria-label="Inactive"
          tooltip-placement="bottom"
        >
          <v-icon :icon="mdiInformationOutline" />
        </span>
        <span
          v-if="item.academicCareerStatus === 'Completed'"
          class="sortable-students-icon"
          uib-tooltip="Graduated"
          aria-label="Graduated"
          tooltip-placement="bottom"
        >
          <v-icon :icon="mdiSchool" />
        </span>
      </div>
    </template>

    <template #item.sid="{item}">
      <span class="sr-only">S I D </span>
      <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ item.sid }}</span>
    </template>

    <template v-if="!options.compact" #item.major="{item}">
      <span class="sr-only">Major</span>
      <div v-if="!item.majors || item.majors.length === 0">--<span class="sr-only">No data</span></div>
      <div v-for="major in item.majors" :key="major">{{ major }}</div>
    </template>

    <template v-if="!options.compact" #item.expectedGraduationTerm="{item}">
      <span class="sr-only">Expected graduation term</span>
      <div v-if="!item.expectedGraduationTerm">--<span class="sr-only">No data</span></div>
      <span class="text-no-wrap">{{ abbreviateTermName(item.expectedGraduationTerm && item.expectedGraduationTerm.name) }}</span>
    </template>

    <template v-if="!options.compact" #item.enrolledUnits="{item}">
      <span class="sr-only">Term units</span>
      {{ _get(item.term, 'enrolledUnits', 0) }}
    </template>

    <template v-if="!options.compact" #item.cumulativeUnits="{item}">
      <span class="sr-only">Units completed</span>
      <div v-if="!item.cumulativeUnits">--<span class="sr-only">No data</span></div>
      <div v-if="item.cumulativeUnits">{{ numFormat(item.cumulativeUnits, '0.00') }}</div>
    </template>

    <template v-if="!options.compact" #item.cumulativeGPA="{item}">
      <span class="sr-only">GPA</span>
      <div v-if="_isNil(item.cumulativeGPA)">--<span class="sr-only">No data</span></div>
      <div v-if="!_isNil(item.cumulativeGPA)">{{ round(item.cumulativeGPA, 3) }}</div>
    </template>

    <template #item.alertCount="{item}">
      <span class="sr-only">Issue count</span>
      <PillAlert
        :aria-label="`${item.alertCount || 'No'} alerts for ${item.name}`"
        :color="item.alertCount ? 'grey' : 'warning'"
        outlined
      >
        {{ item.alertCount || 0 }}
      </PillAlert>
    </template>
  </v-data-table-virtual>
</template>

<script setup>
import {displayAsAscInactive, displayAsCoeInactive} from '@/berkeley'
import {mdiSchool, mdiInformationOutline} from '@mdi/js'
import {useContextStore} from '@/stores/context'
</script>

<script>
import Context from '@/mixins/Context'
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import PillAlert from '@/components/util/PillAlert'
import StudentAvatar from '@/components/student/StudentAvatar'
import Util from '@/mixins/Util'
import {find, get, isNil, isNumber} from 'lodash'
import {sortComparator} from '@/lib/utils'

export default {
  name: 'SortableStudents',
  components: {
    CuratedStudentCheckbox,
    ManageStudent,
    PillAlert,
    StudentAvatar
  },
  mixins: [Context, Util],
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
    headers: undefined,
    sortBy: undefined,
    sortDescending: undefined,
    stackTable: false
  }),
  watch: {
    sortBy() {
      this.onChangeSortBy()
    },
    sortDescending() {
      this.onChangeSortBy()
    }
  },
  mounted() {
    this.onResize()
  },
  created() {
    this.sortBy = this.options.sortBy
    this.sortDescending = this.options.reverse
    this.headers = []
    if (this.options.includeCuratedCheckbox) {
      this.headers.push({align: 'start', cellProps: {width: 0}, key: 'curated', sortable: false, value: 'curated', headerProps: {width: 0}})
    }
    const sortable = this.students.length > 1
    this.headers = this.headers.concat([
      {align: 'start', key: 'avatar', sortable: false, title: 'Photo', value: 'photo'},
      {key: 'name', sortable, title: 'Name', value: 'lastName'},
      {key: 'sid', sortable, title: 'SID', value: 'sid'}
    ])
    if (this.options.compact) {
      this.headers.push({key: 'alertCount', sortable, title: 'Alerts', value: 'alertCount'})
    } else {
      this.headers = this.headers.concat([
        {key: 'major', sortable, title: 'Major', value: 'majors[0]'},
        {key: 'expectedGraduationTerm', sortable, title: 'Grad', value: 'expectedGraduationTerm.id'},
        {key: 'enrolledUnits', sortable, title: 'Term units', value: 'term.enrolledUnits'},
        {key: 'cumulativeUnits', sortable, title: 'Units completed', value: 'cumulativeUnits'},
        {key: 'cumulativeGPA', sortable, title: 'GPA', value: 'cumulativeGPA'},
        {align: 'end', key: 'alertCount', sortable, title: 'Alerts', value: 'alertCount'}
      ])
    }
  },
  methods: {
    abbreviateTermName: termName => termName && termName.replace('20', ' \'').replace('Spring', 'Spr').replace('Summer', 'Sum'),
    normalizeForSort: value => this._isString(value) ? value.toLowerCase() : value,
    onChangeSortBy() {
      const field = find(this.headers, ['value', get(this.sortBy, 0)])
      if (field) {
        this.alertScreenReader(`Sorted by ${field.title}${this.sortDescending ? ', descending' : ''}`)
      }
    },
    onResize() {
      this.stackTable = this.$vuetify.display.mdAndDown
    },
    sortCompare(a, b, sortBy, sortDesc) {
      let aValue = get(a, sortBy)
      let bValue = get(b, sortBy)
      // If column type is number then nil is treated as zero.
      aValue = isNil(aValue) && isNumber(bValue) ? 0 : this.normalizeForSort(aValue)
      bValue = isNil(bValue) && isNumber(aValue) ? 0 : this.normalizeForSort(bValue)
      let result = sortComparator(aValue, bValue)
      if (result === 0) {
        this._each(['lastName', 'firstName', 'sid'], field => {
          result = sortComparator(
            this.normalizeForSort(get(a, field)),
            this.normalizeForSort(get(b, field))
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
