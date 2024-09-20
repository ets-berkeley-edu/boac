<template>
  <v-data-table-virtual
    :cell-props="data => ({
      class: 'pl-0',
      'data-label': data.column.title,
      id: `td-admit-${data.item.csEmplId}-column-${data.column.key}`,
      style: $vuetify.display.mdAndUp ? 'max-width: 200px;' : ''
    })"
    class="responsive-data-table v-table-hidden-row-override"
    density="compact"
    :header-props="{class: 'pl-0 text-no-wrap'}"
    :headers="headers"
    :items="admittedStudents"
    mobile-breakpoint="md"
    must-sort
    no-sort-reset
    :row-props="data => ({
      id: `tr-admit-${data.item.csEmplId}`
    })"
    @update:sort-by="onUpdateSortBy"
  >
    <template #headers="{columns, isSorted, toggleSort, getSortIcon}">
      <tr>
        <th
          v-for="column in columns"
          :key="column.key"
          :aria-label="column.ariaLabel || column.title"
          :aria-sort="isSorted(column) ? `${sortBy.order}ending` : null"
          class="pl-0 text-no-wrap text-left"
          :style="column.headerProps"
        >
          <template v-if="column.sortable">
            <v-btn
              :id="`admits-sort-by-${column.key}-btn`"
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
            <div
              :aria-hidden="!!column.ariaLabel"
              class="not-sortable font-size-12 font-weight-bold text-body"
              :class="get(column, 'headerProps.class', '')"
            >
              {{ column.title }}
            </div>
            <span v-if="!!column.ariaLabel" class="sr-only">{{ column.ariaLabel }}</span>
          </template>
        </th>
      </tr>
    </template>

    <template #item.curated="{item}">
      <CuratedStudentCheckbox
        domain="admitted_students"
        :student="item"
      />
    </template>

    <template #item.lastName="{item}">
      <span class="sr-only">Admitted student name</span>
      <router-link
        :id="`link-to-admit-${item.csEmplId}`"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        :to="admitRoutePath(item.csEmplId)"
        v-html="fullName(item)"
      />
    </template>

    <template #item.csEmplId="{item}">
      <span class="sr-only">C S I D<span aria-hidden="true">&nbsp;</span></span>
      <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ item.csEmplId }}</span>
    </template>

    <template #item.currentSir="{item}">
      <span class="sr-only">S I R</span>
      {{ item.currentSir }}
    </template>

    <template #item.specialProgramCep="{item}">
      <span class="sr-only">C E P</span>
      {{ item.specialProgramCep || '&mdash;' }}
    </template>

    <template #item.reentryStatus="{item}">
      <span class="sr-only">Re-entry</span>
      {{ item.reentryStatus }}
    </template>

    <template #item.firstGenerationCollege="{item}">
      <span class="sr-only">First generation</span>
      {{ item.firstGenerationCollege }}
    </template>

    <template #item.urem="{item}">
      <span class="sr-only">U R E M</span>
      {{ item.urem }}
    </template>

    <template #item.applicationFeeWaiverFlag="{item}">
      <span class="sr-only">Waiver</span>
      {{ item.applicationFeeWaiverFlag }}
    </template>

    <template #item.residencyCategory="{item}">
      <span class="sr-only">Residency</span>
      {{ item.residencyCategory }}
    </template>

    <template #item.freshmanOrTransfer="{item}">
      <span class="sr-only">Freshman or Transfer</span>
      {{ item.freshmanOrTransfer }}
    </template>
  </v-data-table-virtual>
</template>

<script setup>
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import {alertScreenReader} from '@/lib/utils'
import {concat, find, get, join, map, orderBy, remove} from 'lodash'
import {onMounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  admittedStudents: {
    required: true,
    type: Array
  }
})

const currentUser = useContextStore().currentUser
const headers = [
  {key: 'curated', title: '', sortable: false},
  {key: 'lastName', ariaLabel: 'last name', title: 'Name', sortable: true, width: '220px'},
  {key: 'csEmplId', ariaLabel: 'C S I D', title: 'CS ID', sortable: true},
  {key: 'currentSir', title: 'SIR', sortable: false},
  {key: 'specialProgramCep', ariaLabel: 'C E P', title: 'CEP', sortable: false},
  {key: 'reentryStatus', title: 'Re-entry', sortable: false},
  {key: 'firstGenerationCollege', title: '1st Gen', sortable: false},
  {key: 'urem', ariaLabel: 'U R E M', title: 'UREM', sortable: false},
  {key: 'applicationFeeWaiverFlag', title: 'Waiver', sortable: false},
  {key: 'residencyCategory', title: 'Residency', sortable: false},
  {key: 'freshmanOrTransfer', title: 'Freshman/Transfer', sortable: false},
]
const items = ref(undefined)
const sortBy = ref({})

onMounted(() => {
  onUpdateSortBy([{key: 'lastName', order: 'asc'}])
})

const admitRoutePath = csEmplId => {
  return currentUser.inDemoMode ? `/admit/student/${window.btoa(csEmplId)}` : `/admit/student/${csEmplId}`
}

const fullName = admit => {
  const lastName = admit.lastName ? `${admit.lastName},` : null
  return join(remove([lastName, admit.firstName, admit.middleName]), ' ')
}

const onUpdateSortBy = primarySortBy => {
  const key = primarySortBy[0].key
  const order = primarySortBy[0].order
  const header = find(headers, {key: key})
  const sortKeys = concat(
    primarySortBy,
    {key: 'lastName', order: 'asc'},
    {key: 'firstName', order: 'asc'},
    {key: 'middleName', order: 'asc'},
    {key: 'csEmplId', order: 'asc'}
  )
  sortBy.value = primarySortBy[0]
  items.value = orderBy(props.admittedStudents, map(sortKeys, 'key'), map(sortKeys, 'order'))
  if (header) {
    alertScreenReader(`Sorted by ${header.ariaLabel || header.title}, ${order}ending`)
  }
}
</script>

<style scoped>
.not-sortable {
  opacity: 0.62;
  padding-top: 2px;
}
</style>
