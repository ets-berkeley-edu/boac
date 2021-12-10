<template>
  <table id="cohort-admitted-students" class="border-top-0 table table-sm table-borderless">
    <thead class="sortable-table-header">
      <tr>
        <th v-if="removeStudent" class="pt-3"></th>
        <th class="align-top pt-3">Name</th>
        <th class="align-top pt-3">CS ID</th>
        <th class="align-top pt-3">SIR</th>
        <th class="align-top pt-3">CEP</th>
        <th class="align-top pt-3 text-nowrap">Re-entry</th>
        <th class="align-top pt-3 text-nowrap">1st Gen</th>
        <th class="align-top pt-3">UREM</th>
        <th class="align-top pt-3">Waiver</th>
        <th class="align-top pt-3 text-nowrap">INT'L</th>
        <th class="align-top pt-3">Freshman or Transfer</th>
      </tr>
    </thead>
    <tbody>
      <AdmitStudentRow
        v-for="(student, index) in students"
        :id="`admit-${student.csEmplId}`"
        :key="student.csEmplId"
        :remove-student="removeStudent"
        :row-index="index"
        :sorted-by="$currentUser.preferences.admitSortBy"
        :admit-student="student"
      />
    </tbody>
  </table>
</template>

<script>
import AdmitStudentRow from '@/components/admit/AdmitStudentRow'

export default {
  name: 'AdmitStudentsTable',
  components: {AdmitStudentRow},
  props: {
    removeStudent: {
      required: false,
      default: () => {},
      type: Function
    },
    students: {
      required: true,
      type: Array
    }
  }
}
</script>
