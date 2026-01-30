<template>
  <v-data-table-virtual
    :cell-props="data => ({
      'data-label': data.column.title,
      id: withTableUid(`td-student-${data.item.sid}-column-${data.column.key}`)
    })"
    class="responsive-data-table v-table-hidden-row-override"
    density="compact"
    :headers="headers"
    :items="items"
    must-sort
    :row-props="data => ({
      id: withTableUid(`tr-student-${data.item.sid}`)
    })"
    :sort-by="[sortBy]"
    @update:sort-by="onUpdateSortBy"
  >
    <template #headers="{columns, isSorted, toggleSort, getSortIcon, sortBy: sortedBy}">
      <SortableTableHeader
        v-if="columns.length"
        :columns="columns"
        :id-prefix="tableUid"
        :is-compact="!mdAndUp"
        :is-sorted="isSorted"
        :set-order="onUpdateSortBy"
        :sorted-by="sortedBy[0]"
        :sort-icon="getSortIcon"
        :table-name="tableName"
        :toggle-sort="toggleSort"
      />
    </template>

    <template #item.curated="{item}">
      <CuratedStudentCheckbox
        v-if="includeCuratedCheckbox"
        class="mb-2"
        :domain="domain"
        :student="item"
      />
    </template>

    <template #item.lastName="{item}">
      <div class="align-start d-flex">
        <span class="sr-only">Student name</span>
        <StudentAvatar
          :key="item.sid"
          class="mr-2"
          size="small"
          :student="item"
        />
        <div v-if="includeCuratedCheckbox" class="sr-only">
          <ManageStudent domain="default" :student="item" />
        </div>
        <router-link
          v-if="item.uid"
          :id="withTableUid(`link-to-student-${item.uid}`)"
          class="mr-1"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
          :to="studentRoutePath(item.uid, useContextStore().currentUser.inDemoMode)"
          v-html="lastNameFirst(item)"
        />
        <div
          v-if="!item.uid"
          :id="withTableUid(`student-${item.sid}-has-no-uid`)"
          class="font-weight-500 mr-1"
          :class="{'demo-mode-blur': useContextStore().currentUser.inDemoMode}"
          v-html="lastNameFirst(item)"
        />
        <div
          v-if="item.academicCareerStatus === 'Inactive' || displayAsAscInactive(item) || displayAsCoeInactive(item)"
          aria-label="Inactive"
          class="inactive-info-icon text-error"
        >
          <v-icon :icon="mdiInformation" />
          <v-tooltip activator="parent" location="bottom">
            INACTIVE
          </v-tooltip>
        </div>
        <div
          v-if="item.academicCareerStatus === 'Completed'"
          aria-label="Graduated"
          class="ml-1 sortable-students-icon"
        >
          <v-icon :icon="mdiSchool" />
          <v-tooltip activator="parent" location="bottom">
            GRADUATED
          </v-tooltip>
        </div>
      </div>
    </template>

    <template #item.sid="{item}">
      <span class="sr-only">S I D<span aria-hidden="true">&nbsp;</span></span>
      <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ item.sid }}</span>
    </template>

    <template v-if="!compact" #item.major="{item}">
      <span class="sr-only">Major</span>
      <div v-if="!item.majors || item.majors.length === 0">--<span class="sr-only">No data</span></div>
      <div v-for="major in item.majors" :key="major" class="pr-1">{{ major }}</div>
    </template>

    <template v-if="!compact" #item.expectedGraduationTerm="{item}">
      <span class="sr-only">Expected graduation term</span>
      <div v-if="!item.expectedGraduationTerm">--<span class="sr-only">No data</span></div>
      <span class="text-no-wrap">{{ abbreviateTermName(item.expectedGraduationTerm && item.expectedGraduationTerm.name) }}</span>
    </template>

    <template v-if="!compact" #item.enrolledUnits="{item}">
      <span class="sr-only">Term units</span>
      {{ get(item.term, 'enrolledUnits', 0) }}
    </template>

    <template v-if="!compact" #item.cumulativeUnits="{item}">
      <span class="sr-only">Units completed</span>
      <div v-if="!item.cumulativeUnits">--<span class="sr-only">No data</span></div>
      <div v-if="item.cumulativeUnits">{{ numFormat(item.cumulativeUnits, '0.00') }}</div>
    </template>

    <template v-if="!compact" #item.cumulativeGPA="{item}">
      <span class="sr-only">GPA</span>
      <div v-if="isNil(item.cumulativeGPA)">--<span class="sr-only">No data</span></div>
      <div v-if="!isNil(item.cumulativeGPA)">{{ round(item.cumulativeGPA, 3) }}</div>
    </template>

    <template #item.alertCount="{item}">
      <PillCount
        :id="withTableUid(`student-${item.uid || item.sid}-alert-count`)"
        :aria-label="`${pluralize('alert', item.alertCount, {0: 'No'})} for ${item.firstName} ${item.lastName}`"
        :color="item.alertCount ? 'warning' : 'grey'"
      >
        {{ item.alertCount || 0 }} <span class="sr-only">alerts</span>
      </PillCount>
    </template>
  </v-data-table-virtual>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {each, find, get, isNil, isString} from 'lodash'
import {mdiInformation, mdiSchool} from '@mdi/js'
import {useDisplay} from 'vuetify'
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import PillCount from '@/components/util/PillCount'
import SortableTableHeader from '@/components/util/SortableTableHeader'
import StudentAvatar from '@/components/student/StudentAvatar'
import {alertScreenReader, lastNameFirst, numFormat, pluralize, round, sortComparator, studentRoutePath} from '@/lib/utils'
import {displayAsAscInactive, displayAsCoeInactive} from '@/lib/student'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  compact: {
    required: false,
    type: Boolean
  },
  domain: {
    required: true,
    type: String
  },
  includeCuratedCheckbox: {
    required: false,
    type: Boolean
  },
  initialSortBy: {
    default: () => ({key: 'lastName', order: 'asc'}),
    type: Object
  },
  students: {
    required: true,
    type: Array
  },
  tableUid: {
    required: false,
    type: String,
    default: ''
  },
  tableName: {
    required: false,
    type: String,
    default: ''
  }
})

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const defaultCellClass = {class: 'font-size-15 py-1 pl-1 pr-3 vertical-top'}
const headers = ref([])
const {mdAndUp} = useDisplay()
const items = ref(undefined)
const sortBy = ref([props.initialSortBy])
const withTableUid = suffix => (props.tableUid ? `${props.tableUid}-${suffix}` : suffix)

const defaultCellProps = computed(() => {
  return {cellProps: {...defaultCellClass, style: mdAndUp ? 'max-width: 200px;' : ''}}
})

onMounted(() => {
  items.value = props.students
  if (props.includeCuratedCheckbox) {
    headers.value.push({
      key: 'curated',
      align: 'start',
      cellProps: {...defaultCellClass, width: 0},
      headerProps: {width: 0},
      sortable: false,
      value: 'curated'
    })
  }
  const sortable = props.students.length > 1
  each([
    {key: 'lastName', ...defaultCellProps.value, ariaLabel: 'last name', sortable, sortRaw, title: 'Name', value: 'lastName'},
    {key: 'sid', ...defaultCellProps.value, ariaLabel: 'S I D', sortable, sortRaw, title: 'SID', value: 'sid'}
  ], header => {
    headers.value.push(header)
  })
  const alertCountCellAttributes = {
    key: 'alertCount',
    ariaLabel: 'alert count',
    cellProps: {class: 'font-size-15 text-center vertical-top'},
    isNumber: true,
    sortable,
    sortRaw,
    title: 'Alerts',
    value: 'alertCount'
  }
  if (props.compact) {
    headers.value.push(alertCountCellAttributes)
  } else {
    each([
      {key: 'major', ...defaultCellProps.value, sortable, sortRaw, title: 'Major', value: 'majors[0]'},
      {key: 'expectedGraduationTerm', ...defaultCellProps.value, sortable, sortRaw, title: 'Grad', value: 'expectedGraduationTerm.id'},
      {key: 'enrolledUnits', ...defaultCellProps.value, isNumber: true, sortable, sortRaw, title: 'Term units', value: 'term.enrolledUnits'},
      {key: 'cumulativeUnits', ...defaultCellProps.value, isNumber: true, sortable, sortRaw, title: 'Units completed', value: 'cumulativeUnits'},
      {key: 'cumulativeGPA', ...defaultCellProps.value, isNumber: true, sortable, sortRaw, title: 'GPA', value: 'cumulativeGPA'},
      alertCountCellAttributes
    ], header => {
      headers.value.push(header)
    })
  }
})

const abbreviateTermName = termName => termName && termName.replace('20', ' \'').replace('Spring', 'Spr').replace('Summer', 'Sum')

const normalizeForSort = value => {
  return isString(value) ? value.toLowerCase() : value
}

const onUpdateSortBy = primarySortBy => {
  const key = primarySortBy[0].key
  const header = find(headers.value, {key: key})
  sortBy.value = primarySortBy[0]
  if (header) {
    const tablePart = props.tableName ? ` ${props.tableName}` : ''
    alertScreenReader(`Sorted${tablePart} by ${header.ariaLabel || header.title}, ${sortBy.value.order}ending`)
  }
}

const sortRaw = (a, b) => {
  const header = find(headers.value, {key: sortBy.value.key})
  const isNumber = get(header, 'isNumber', false)
  const sortKey = get(header, 'value', sortBy.value.key)
  const sortDesc = sortBy.value.order === 'desc'
  let aValue = get(a, sortKey)
  let bValue = get(b, sortKey)
  // If column type is number then nil is treated as zero.
  aValue = isNil(aValue) && isNumber ? 0 : normalizeForSort(aValue)
  bValue = isNil(bValue) && isNumber ? 0 : normalizeForSort(bValue)
  let result = sortComparator(aValue, bValue)
  if (result === 0) {
    each(['lastName', 'firstName', 'sid'], field => {
      result = sortComparator(
        normalizeForSort(get(a, field)),
        normalizeForSort(get(b, field))
      )
      // Secondary sort is always ascending
      result *= sortDesc ? -1 : 1
      // Break from loop if comparator result is non-zero
      return result === 0
    })
  }
  return result
}
</script>
