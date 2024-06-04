<template>
  <v-data-table-virtual
    :cell-props="{
      class: 'pl-0 vertical-top',
      style: $vuetify.display.mdAndUp ? 'max-width: 200px;' : ''
    }"
    :header-props="{class: 'pl-0 text-no-wrap'}"
    :headers="headers"
    :items="admittedStudents"
    mobile-breakpoint="md"
    no-sort-reset
    :sort-by="[sortBy]"
    :sort-compare="sortCompare"
    :sort-desc="sortDescending"
  >
    <template #item.curated="{item}">
      <CuratedStudentCheckbox
        class="mb-4"
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

<script>
import Context from '@/mixins/Context'
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import Util from '@/mixins/Util'
import {alertScreenReader, sortComparator} from '@/lib/utils'

export default {
  name: 'SortableAdmits',
  components: {CuratedStudentCheckbox},
  mixins: [Context, Util],
  props: {
    admittedStudents: {
      required: true,
      type: Array
    }
  },
  data() {
    return {
      headers: undefined,
      sortBy: 'lastName',
      sortDescending: false
    }
  },
  watch: {
    sortBy() {
      this.onChangeSortBy()
    },
    sortDescending() {
      this.onChangeSortBy()
    }
  },
  created() {
    this.headers = [
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
  },
  methods: {
    admitRoutePath(csEmplId) {
      return this.currentUser.inDemoMode ? `/admit/student/${window.btoa(csEmplId)}` : `/admit/student/${csEmplId}`
    },
    fullName(admit) {
      const lastName = admit.lastName ? `${admit.lastName},` : null
      return this._join(this._remove([lastName, admit.firstName, admit.middleName]), ' ')
    },
    normalizeForSort(value) {
      return this._isString(value) ? value.toLowerCase() : value
    },
    onChangeSortBy() {
      const header = this._find(this.headers, ['key', this.sortBy])
      alertScreenReader(`Sorted by ${header.title}${this.sortDescending ? ', descending' : ''}`)
    },
    sortCompare(a, b, sortBy, sortDesc) {
      let aValue = this.normalizeForSort(this._get(a, sortBy))
      let bValue = this.normalizeForSort(this._get(b, sortBy))
      let result = sortComparator(aValue, bValue)
      if (result === 0) {
        this._each(['lastName', 'firstName', 'csEmplId'], field => {
          result = sortComparator(
            this.normalizeForSort(this._get(a, field)),
            this.normalizeForSort(this._get(b, field))
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
