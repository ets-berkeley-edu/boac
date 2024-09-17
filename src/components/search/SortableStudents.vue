<template>
  <v-data-table-virtual
    :cell-props="data => ({
      class: 'pl-0 vertical-top',
      'data-label': data.column.title,
      id: `td-student-${data.item.sid}-column-${data.column.key}`,
      style: $vuetify.display.mdAndUp ? 'max-width: 200px;' : ''
    })"
    class="responsive-data-table"
    density="compact"
    :headers="headers"
    :header-props="{class: 'pl-0'}"
    :items="items"
    mobile-breakpoint="md"
    must-sort
    :row-props="data => ({
      id: `tr-student-${data.item.sid}`
    })"
    @update:sort-by="onUpdateSortBy"
  >
    <template #header.avatar="{column}">
      <span class="sr-only">{{ column.title }}</span>
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
      <div class="align-center d-flex">
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
import {concat, each, get, isNil, map, orderBy} from 'lodash'
import {displayAsAscInactive, displayAsCoeInactive} from '@/berkeley'
import {mdiSchool, mdiInformation} from '@mdi/js'
import {onMounted, ref} from 'vue'
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
  sortBy: {
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
const headers = ref([])
const items = ref(undefined)

onMounted(() => {
  onUpdateSortBy([props.sortBy])
  if (props.includeCuratedCheckbox) {
    headers.value.push({align: 'start', cellProps: {width: 0}, key: 'curated', sortable: false, value: 'curated', headerProps: {width: 0}})
  }
  const sortable = props.students.length > 1
  each([
    {align: 'start', key: 'avatar', sortable: false, title: 'Photo', value: 'photo'},
    {key: 'lastName', sortable, title: 'Name', value: 'lastName'},
    {key: 'sid', sortable, title: 'SID', value: 'sid'}
  ], header => {
    headers.value.push(header)
  })
  if (props.compact) {
    headers.value.push({key: 'alertCount', sortable, title: 'Alerts', value: 'alertCount'})
  } else {
    each([
      {key: 'major', sortable, title: 'Major', value: 'majors[0]'},
      {key: 'expectedGraduationTerm', sortable, title: 'Grad', value: 'expectedGraduationTerm.id'},
      {key: 'enrolledUnits', sortable, title: 'Term units', value: 'term.enrolledUnits'},
      {key: 'cumulativeUnits', sortable, title: 'Units completed', value: 'cumulativeUnits'},
      {key: 'cumulativeGPA', sortable, title: 'GPA', value: 'cumulativeGPA'},
      {align: 'end', class: 'alert-count', key: 'alertCount', sortable, title: 'Alerts', value: 'alertCount'}
    ], header => {
      headers.value.push(header)
    })
  }
})

const abbreviateTermName = termName => termName && termName.replace('20', ' \'').replace('Spring', 'Spr').replace('Summer', 'Sum')

const onUpdateSortBy = primarySortBy => {
  const sortBy = concat(
    primarySortBy,
    {key: 'lastName', order: 'asc'},
    {key: 'firstName', order: 'asc'},
    {key: 'sid', order: 'asc'}
  )
  items.value = orderBy(props.students, map(sortBy, 'key'), map(sortBy, 'order'))
  const key = primarySortBy[0].key
  if (key in map(headers.value, 'key')) {
    const header = headers.value.get(key)
    alertScreenReader(`Sorted by ${header.title}, ${primarySortBy[0].order}ending`)
  }
}
</script>
