<template>
  <v-data-table-virtual
    :cell-props="data => ({
      'data-label': data.column.title,
      id: `td-student-${data.item.sid}-column-${data.column.key}`
    })"
    class="responsive-data-table v-table-hidden-row-override"
    density="compact"
    :headers="headers"
    :items="items"
    mobile-breakpoint="md"
    must-sort
    :row-props="data => ({
      id: `tr-student-${data.item.sid}`
    })"
    :sort-by="[sortBy]"
    @update:sort-by="onUpdateSortBy"
  >
    <template #headers="{columns, isSorted, toggleSort, getSortIcon}">
      <tr>
        <th
          v-for="column in columns"
          :key="column.key"
          :aria-label="column.ariaLabel || column.title"
          :aria-sort="isSorted(column) ? `${sortBy.order}ending` : null"
          class="pl-0 pr-3 text-left"
          :style="column.headerProps"
        >
          <template v-if="column.sortable">
            <v-btn
              :id="`students-sort-by-${column.key}-btn`"
              :append-icon="getSortIcon(column)"
              :aria-label="`Sort by ${column.ariaLabel || column.title} ${isSorted(column) && sortBy.order === 'asc' ? 'descending' : 'ascending'}`"
              class="align-start font-size-12 font-weight-bold height-unset min-width-unset pa-1 text-uppercase v-table-sort-btn-override"
              :class="{'icon-visible': isSorted(column)}"
              color="body"
              density="compact"
              variant="plain"
              @click="() => toggleSort(column)"
            >
              <span class="text-left text-wrap">{{ column.title }}</span>
            </v-btn>
          </template>
          <template v-else>
            <span :class="get(column, 'headerProps.class', '')">{{ column.title }}</span>
          </template>
        </th>
      </tr>
    </template>

    <template #item.curated="{item}">
      <CuratedStudentCheckbox
        v-if="includeCuratedCheckbox"
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
      <div v-if="includeCuratedCheckbox" class="sr-only">
        <ManageStudent domain="default" :student="item" />
      </div>
    </template>

    <template #item.lastName="{item}">
      <div class="align-start d-flex">
        <span class="sr-only">Student name</span>
        <router-link
          v-if="item.uid"
          :id="`link-to-student-${item.uid}`"
          class="mr-1"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
          :to="studentRoutePath(item.uid, useContextStore().currentUser.inDemoMode)"
          v-html="lastNameFirst(item)"
        />
        <div
          v-if="!item.uid"
          :id="`student-${item.sid}-has-no-uid`"
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
        :id="`student-${item.uid}-alert-count`"
        :aria-label="`${pluralize('alert', item.alertCount, {0: 'No'})} for ${item.firstName} ${item.lastName}`"
        :color="item.alertCount ? 'warning' : 'grey'"
      >
        {{ item.alertCount || 0 }} <span class="sr-only">alerts</span>
      </PillCount>
    </template>
  </v-data-table-virtual>
</template>

<script setup>
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import PillCount from '@/components/util/PillCount'
import StudentAvatar from '@/components/student/StudentAvatar'
import {alertScreenReader, lastNameFirst, numFormat, pluralize, round, studentRoutePath} from '@/lib/utils'
import {computed, onMounted, ref} from 'vue'
import {each, find, get, isNil, isString} from 'lodash'
import {displayAsAscInactive, displayAsCoeInactive} from '@/berkeley'
import {mdiSchool, mdiInformation} from '@mdi/js'
import {sortComparator} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useDisplay} from 'vuetify'

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
  }
})

const contextStore = useContextStore()

const currentUser = contextStore.currentUser
const defaultCellClass = {class: 'font-size-15 py-1 pl-1 pr-3 vertical-top'}
const defaultCellProps = computed(() => {
  return {cellProps: {...defaultCellClass, style: useDisplay().mdAndUp ? 'max-width: 200px;' : ''}}
})
const headers = ref([])
const items = ref(undefined)
const sortBy = ref({})

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
    {
      key: 'avatar',
      align: 'start',
      ...defaultCellProps.value,
      headerProps: {class: 'sr-only'},
      sortable: false,
      title: 'Photo',
      value: 'photo'
    },
    {key: 'lastName', ...defaultCellProps.value, ariaLabel: 'last name', sortable, sortRaw, title: 'Name', value: 'lastName'},
    {key: 'sid', ...defaultCellProps.value, ariaLabel: 'S I D', sortable, sortRaw, title: 'SID', value: 'sid'}
  ], header => {
    headers.value.push(header)
  })
  if (props.compact) {
    headers.value.push({key: 'alertCount', ...defaultCellProps.value, isNumber: true, sortable, sortRaw, title: 'Alerts', value: 'alertCount'})
  } else {
    each([
      {key: 'major', ...defaultCellProps.value, sortable, sortRaw, title: 'Major', value: 'majors[0]'},
      {key: 'expectedGraduationTerm', ...defaultCellProps.value, sortable, sortRaw, title: 'Grad', value: 'expectedGraduationTerm.id'},
      {key: 'enrolledUnits', ...defaultCellProps.value, isNumber: true, sortable, sortRaw, title: 'Term units', value: 'term.enrolledUnits'},
      {key: 'cumulativeUnits', ...defaultCellProps.value, isNumber: true, sortable, sortRaw, title: 'Units completed', value: 'cumulativeUnits'},
      {key: 'cumulativeGPA', ...defaultCellProps.value, isNumber: true, sortable, sortRaw, title: 'GPA', value: 'cumulativeGPA'},
      {
        key: 'alertCount',
        align: 'end',
        cellProps: {class: 'py-1 pl-1 pr-2 vertical-top'},
        isNumber: true,
        sortable,
        sortRaw,
        title: 'Alerts',
        value: 'alertCount'
      }
    ], header => {
      headers.value.push(header)
    })
  }
  sortBy.value = props.initialSortBy
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
    alertScreenReader(`Sorted by ${header.ariaLabel || header.title}, ${sortBy.value.order}ending`)
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

<style scoped>
.height-unset {
  height: unset !important;
}
</style>
