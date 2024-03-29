<template>
  <div>
    <b-table
      :borderless="true"
      :fields="fields"
      :items="admittedStudents"
      :no-sort-reset="true"
      :small="true"
      :sort-by.sync="sortBy"
      :sort-compare="sortCompare"
      :sort-desc.sync="sortDescending"
      stacked="md"
      thead-class="sortable-table-header text-no-wrap"
    >
      <template #cell(curated)="row">
        <CuratedStudentCheckbox
          domain="admitted_students"
          :student="row.item"
        />
      </template>

      <template #cell(lastName)="row">
        <span class="sr-only">Admitted student name</span>
        <router-link
          :id="`link-to-admit-${row.item.csEmplId}`"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
          :to="admitRoutePath(row.item.csEmplId)"
          v-html="fullName(row.item)"
        ></router-link>
      </template>

      <template #cell(csEmplId)="row">
        <span class="sr-only">C S I D </span>
        <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ row.item.csEmplId }}</span>
      </template>

      <template #cell(currentSir)="row">
        <span class="sr-only">S I R</span>
        {{ row.item.currentSir }}
      </template>

      <template #cell(specialProgramCep)="row">
        <span class="sr-only">C E P</span>
        {{ row.item.specialProgramCep }}
      </template>

      <template #cell(reentryStatus)="row">
        <span class="sr-only">Re-entry</span>
        {{ row.item.reentryStatus }}
      </template>

      <template #cell(firstGenerationCollege)="row">
        <span class="sr-only">First generation</span>
        {{ row.item.firstGenerationCollege }}
      </template>

      <template #cell(urem)="row">
        <span class="sr-only">U R E M</span>
        {{ row.item.urem }}
      </template>

      <template #cell(applicationFeeWaiverFlag)="row">
        <span class="sr-only">Waiver</span>
        {{ row.item.applicationFeeWaiverFlag }}
      </template>

      <template #cell(residencyCategory)="row">
        <span class="sr-only">Residency</span>
        {{ row.item.residencyCategory }}
      </template>

      <template #cell(freshmanOrTransfer)="row">
        <span class="sr-only">Freshman or Transfer</span>
        {{ row.item.freshmanOrTransfer }}
      </template>
    </b-table>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import Util from '@/mixins/Util'
import {sortComparator} from '@/lib/utils'

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
      fields: undefined,
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
    this.fields = [
      {key: 'curated', label: ''},
      {key: 'lastName', label: 'Name', sortable: true},
      {key: 'csEmplId', label: 'CS ID', sortable: true},
      {key: 'currentSir', label: 'SIR', sortable: false},
      {key: 'specialProgramCep', label: 'CEP', sortable: false},
      {key: 'reentryStatus', label: 'Re-entry', sortable: false},
      {key: 'firstGenerationCollege', label: '1st Gen', sortable: false},
      {key: 'urem', label: 'UREM', sortable: false},
      {key: 'applicationFeeWaiverFlag', label: 'Waiver', sortable: false},
      {key: 'residencyCategory', label: 'Residency', sortable: false},
      {key: 'freshmanOrTransfer', label: 'Freshman/Transfer', sortable: false},
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
      const field = this._find(this.fields, ['key', this.sortBy])
      this.alertScreenReader(`Sorted by ${field.label}${this.sortDescending ? ', descending' : ''}`)
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
