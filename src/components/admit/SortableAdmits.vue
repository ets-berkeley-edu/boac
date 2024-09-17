<template>
  <v-data-table-virtual
    :cell-props="data => ({
      class: 'pl-0',
      'data-label': data.column.title,
      id: `td-admit-${data.item.csEmplId}-column-${data.column.key}`,
      style: $vuetify.display.mdAndUp ? 'max-width: 200px;' : ''
    })"
    class="responsive-data-table"
    density="compact"
    :header-props="{class: 'pl-0 text-no-wrap'}"
    :headers="headers"
    :items="admittedStudents"
    mobile-breakpoint="md"
    no-sort-reset
    :row-props="data => ({
      id: `tr-admit-${data.item.csEmplId}`
    })"
    :sort-by="[sortBy]"
    :sort-compare="sortCompare"
    :sort-desc="sortDescending"
  >
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
import {alertScreenReader, sortComparator} from '@/lib/utils'
import {each, find, get, isString, join, remove} from 'lodash'
import {ref, watch} from 'vue'
import {useContextStore} from '@/stores/context'

defineProps({
  admittedStudents: {
    required: true,
    type: Array
  }
})

const currentUser = useContextStore().currentUser
const headers = [
  {key: 'curated', title: ''},
  {key: 'lastName', title: 'Name', sortable: true, width: '220px'},
  {key: 'csEmplId', title: 'CS ID', sortable: true},
  {key: 'currentSir', title: 'SIR', sortable: false},
  {key: 'specialProgramCep', title: 'CEP', sortable: false},
  {key: 'reentryStatus', title: 'Re-entry', sortable: false},
  {key: 'firstGenerationCollege', title: '1st Gen', sortable: false},
  {key: 'urem', title: 'UREM', sortable: false},
  {key: 'applicationFeeWaiverFlag', title: 'Waiver', sortable: false},
  {key: 'residencyCategory', title: 'Residency', sortable: false},
  {key: 'freshmanOrTransfer', title: 'Freshman/Transfer', sortable: false},
]
const sortBy = ref('lastName')
const sortDescending = ref(false)

watch(sortBy, () => {
  onChangeSortBy()
})
watch(sortDescending, () => {
  onChangeSortBy()
})

const admitRoutePath = csEmplId => {
  return currentUser.inDemoMode ? `/admit/student/${window.btoa(csEmplId)}` : `/admit/student/${csEmplId}`
}

const fullName = admit => {
  const lastName = admit.lastName ? `${admit.lastName},` : null
  return join(remove([lastName, admit.firstName, admit.middleName]), ' ')
}

const normalizeForSort = value => {
  return isString(value) ? value.toLowerCase() : value
}

const onChangeSortBy = () => {
  const header = find(headers, ['key', sortBy.value])
  alertScreenReader(`Sorted by ${header.title}${sortDescending.value ? ', descending' : ''}`)
}

const sortCompare = (a, b, sortBy, sortDesc) => {
  let aValue = normalizeForSort(get(a, sortBy))
  let bValue = normalizeForSort(get(b, sortBy))
  let result = sortComparator(aValue, bValue)
  if (result === 0) {
    each(['lastName', 'firstName', 'csEmplId'], field => {
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
