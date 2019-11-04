<template>
  <div>
    <div class="modal-header">
      <h3 id="export-list-header">Export List</h3>
    </div>
    <div id="export-list-body" class="modal-body">
      <b-form-group>
        <b-form-checkbox-group
          id="csv-column-options"
          :options="csvColumns"
          v-model="csvColumnsSelected"
          class="flex-col flex-wrap csv-column-options"
          name="csv-column-options"
          stacked>
        </b-form-checkbox-group>
      </b-form-group>
    </div>
    <div class="modal-footer">
      <form @submit.prevent="exportList(csvColumnsSelected)">
        <b-btn
          id="export-list-confirm"
          @click.prevent="exportList(csvColumnsSelected)"
          class="btn-primary-color-override"
          variant="primary">
          Export
        </b-btn>
        <b-btn
          id="export-list-cancel"
          @click="cancelExportListModal()"
          class="pl-2"
          variant="link">
          Close
        </b-btn>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExportListModal',
  props: {
    cancelExportListModal: Function,
    exportList: Function
  },
  data: () => ({
    csvColumns: [
      {text: 'First name', value: 'first_name'},
      {text: 'Last name', value: 'last_name'},
      {text: 'SID', value: 'sid'},
      {text: 'Email address', value: 'email'},
      {text: 'Phone number', value: 'phone'},
      {text: 'Major(s)', value: 'majors'},
      {text: 'Level', value: 'level'},
      {text: 'Terms in attendance', value: 'terms_in_attendance'},
      {text: 'Expected graduation date', value: 'expected_graduation_date'},
      {text: 'Units completed', value: 'units_completed'},
      {text: 'Term GPA', value: 'term_gpa'},
      {text: 'Cumulative GPA', value: 'cumulative_gpa'},
      {text: 'Program status', value: 'program_status'}
    ],
    csvColumnsSelected: ['first_name', 'last_name', 'sid', 'email', 'phone']
  })
};
</script>

<style scoped>
.csv-column-options {
  height: 200px;
}
</style>
