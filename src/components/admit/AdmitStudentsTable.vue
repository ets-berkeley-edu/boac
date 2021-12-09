<template>
  <table id="cohort-admitted-students" class="table table-sm table-borderless cohort-admitted-students mx-2">
    <thead class="sortable-table-header">
      <tr>
        <th class="pt-3">Name</th>
        <th class="pt-3">CS ID</th>
        <th class="pt-3">SIR</th>
        <th class="pt-3">CEP</th>
        <th class="pt-3">Re-entry</th>
        <th class="pt-3">1st Gen</th>
        <th class="pt-3">UREM</th>
        <th class="pt-3">Waiver</th>
        <th class="pt-3">INT'L</th>
        <th class="pt-3">Freshman/Transfer</th>
      </tr>
    </thead>
    <tbody>
      <AdmitStudentRow
        v-for="(student, index) in students"
        :id="`admit-${student.csEmplId}`"
        :key="student.csEmplId"
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
  props: {
    students: {
      required: true,
      type: Array
    }
  },
  components: {AdmitStudentRow}
}
</script>
