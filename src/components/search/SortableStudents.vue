<template>
  <v-data-table-virtual
    :cell-props="data => ({
      class: 'pl-0 vertical-top',
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
          class="mr-1 text-primary"
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
          <v-icon :icon="mdiInformationOutline" />
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
      <div v-for="major in item.majors" :key="major">{{ major }}</div>
    </template>

    <template v-if="!compact" #item.expectedGraduationTerm="{item}">
      <span class="sr-only">Expected graduation term</span>
      <div v-if="!item.expectedGraduationTerm">--<span class="sr-only">No data</span></div>
      <span class="text-no-wrap">{{ abbreviateTermName(item.expectedGraduationTerm && item.expectedGraduationTerm.name) }}</span>
    </template>

    <template v-if="!compact" #item.enrolledUnits="{item}">
      <span class="sr-only">Term units</span>
      {{ _get(item.term, 'enrolledUnits', 0) }}
    </template>

    <template v-if="!compact" #item.cumulativeUnits="{item}">
      <span class="sr-only">Units completed</span>
      <div v-if="!item.cumulativeUnits">--<span class="sr-only">No data</span></div>
      <div v-if="item.cumulativeUnits">{{ numFormat(item.cumulativeUnits, '0.00') }}</div>
    </template>

    <template v-if="!compact" #item.cumulativeGPA="{item}">
      <span class="sr-only">GPA</span>
      <div v-if="_isNil(item.cumulativeGPA)">--<span class="sr-only">No data</span></div>
      <div v-if="!_isNil(item.cumulativeGPA)">{{ round(item.cumulativeGPA, 3) }}</div>
    </template>

    <template #item.alertCount="{item}">
      <PillAlert
        :aria-label="`${item.alertCount || 'No'} alerts for ${item.firstName} ${item.lastName}`"
        :color="item.alertCount ? 'warning' : 'grey'"
        outlined
      >
        {{ item.alertCount || 0 }} <span class="sr-only">alerts</span>
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
import {alertScreenReader} from '@/lib/utils'
import {concat, map, orderBy} from 'lodash'

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
  },
  data: () => ({
    headers: undefined,
    items: undefined
  }),
  created() {
    this.onUpdateSortBy([this.sortBy])
    this.headers = []
    if (this.includeCuratedCheckbox) {
      this.headers.push({align: 'start', cellProps: {width: 0}, key: 'curated', sortable: false, value: 'curated', headerProps: {width: 0}})
    }
    const sortable = this.students.length > 1
    this.headers = this.headers.concat([
      {align: 'start', key: 'avatar', sortable: false, title: 'Photo', value: 'photo'},
      {key: 'lastName', sortable, title: 'Name', value: 'lastName'},
      {key: 'sid', sortable, title: 'SID', value: 'sid'}
    ])
    if (this.compact) {
      this.headers.push({key: 'alertCount', sortable, title: 'Alerts', value: 'alertCount'})
    } else {
      this.headers = this.headers.concat([
        {key: 'major', sortable, title: 'Major', value: 'majors[0]'},
        {key: 'expectedGraduationTerm', sortable, title: 'Grad', value: 'expectedGraduationTerm.id'},
        {key: 'enrolledUnits', sortable, title: 'Term units', value: 'term.enrolledUnits'},
        {key: 'cumulativeUnits', sortable, title: 'Units completed', value: 'cumulativeUnits'},
        {key: 'cumulativeGPA', sortable, title: 'GPA', value: 'cumulativeGPA'},
        {align: 'end', class: 'alert-count', key: 'alertCount', sortable, title: 'Alerts', value: 'alertCount'}
      ])
    }
  },
  methods: {
    abbreviateTermName: termName => termName && termName.replace('20', ' \'').replace('Spring', 'Spr').replace('Summer', 'Sum'),
    onUpdateSortBy(primarySortBy) {
      const sortBy = concat(
        primarySortBy,
        {key: 'lastName', order: 'asc'},
        {key: 'firstName', order: 'asc'},
        {key: 'sid', order: 'asc'}
      )
      this.items = orderBy(this.students, map(sortBy, 'key'), map(sortBy, 'order'))
      const key = primarySortBy[0].key
      if (key in map(this.headers, 'key')) {
        const header = this.headers.get(key)
        alertScreenReader(`Sorted by ${header.title}, ${primarySortBy[0].order}ending`)
      }
    }
  }
}
</script>
