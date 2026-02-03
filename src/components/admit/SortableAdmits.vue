<template>
  <v-data-table-virtual
    v-table-caption="tableCaption"
    :cell-props="data => ({
      class: 'pl-0',
      'data-label': data.column.title,
      id: `td-admit-${data.item.csEmplId}-column-${data.column.key}`
    })"
    class="v-table-hidden-row-override"
    :class="{'stacked-table': $vuetify.display.width <= mobileBreakpoint}"
    density="compact"
    :headers="headers"
    :items="admittedStudents"
    must-sort
    no-sort-reset
    :row-props="data => ({
      id: `tr-admit-${data.item.csEmplId}`
    })"
    :sort-by="[sortBy]"
    @update:sort-by="onUpdateSortBy"
  >
    <template #headers="{columns, isSorted, toggleSort, getSortIcon, sortBy: sortedBy}">
      <SortableTableHeader
        v-if="columns.length"
        :columns="columns"
        id-prefix="admits"
        :is-compact="$vuetify.display.width <= mobileBreakpoint"
        :is-sorted="isSorted"
        :set-order="onUpdateSortBy"
        :sorted-by="sortedBy[0]"
        :sort-icon="getSortIcon"
        :toggle-sort="toggleSort"
      />
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
import {concat, find, join, map, orderBy, remove} from 'lodash'
import {computed, onMounted, ref} from 'vue'
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import SortableTableHeader from '@/components/util/SortableTableHeader'
import {alertScreenReader} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  admittedStudents: {
    required: true,
    type: Array
  },
  tableName: {
    required: false,
    type: String,
    default: ''
  }
})

const currentUser = useContextStore().currentUser
const headers = [
  {key: 'curated', ariaLabel: 'select', sortable: false},
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
const mobileBreakpoint = 1070
const sortBy = ref({})

const tableCaption = computed(() =>
  props.tableName ? `Admit students table: ${props.tableName}` : 'Admit students table'
)

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

<style scoped lang="scss">
$boa-breakpoint: 1070px !important;
</style>
