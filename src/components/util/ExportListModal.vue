<template>
  <div>
    <div class="modal-header">
      <h3 id="export-list-header">Export List</h3>
    </div>
    <div id="export-list-body" class="modal-body">
      <b-form-group>
        <b-form-checkbox-group
          id="csv-column-options"
          v-model="selected"
          :options="csvColumns"
          class="flex-col flex-wrap csv-column-options"
          name="csv-column-options"
          stacked>
        </b-form-checkbox-group>
      </b-form-group>
    </div>
    <div class="modal-footer">
      <form @submit.prevent="exportList(selected)">
        <b-btn
          id="export-list-confirm"
          :disabled="!selected.length"
          class="btn-primary-color-override"
          variant="primary"
          @click.prevent="exportList(selected)">
          Export
        </b-btn>
        <b-btn
          id="export-list-cancel"
          class="pl-2"
          variant="link"
          @click="cancelExportListModal">
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
    cancelExportListModal: {
      required: true,
      type: Function
    },
    csvColumns: {
      required: true,
      type: Array
    },
    csvColumnsSelected: {
      type: Array
    },
    exportList: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    selected: []
  }),
  created() {
    this.selected = this.csvColumnsSelected;
  }
};
</script>

<style scoped>
.csv-column-options {
  height: 200px;
}
</style>
