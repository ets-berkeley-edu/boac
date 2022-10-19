<template>
  <div>
    <ModalHeader text="Export List" />
    <div id="export-list-body" class="modal-body">
      <b-form-group>
        <b-form-checkbox-group
          id="csv-column-options"
          v-model="selected"
          :options="csvColumns"
          class="flex-col flex-wrap csv-column-options"
          name="csv-column-options"
          stacked
        >
        </b-form-checkbox-group>
      </b-form-group>
      <div class="px-1">
        <span class="font-weight-700">Reminder:</span> <FerpaReminder />
      </div>
    </div>
    <div class="modal-footer">
      <form @submit.prevent="onSubmit">
        <b-btn
          id="export-list-confirm"
          :disabled="!selected.length"
          class="btn-primary-color-override"
          variant="primary"
          @click.prevent="onSubmit"
        >
          Export
        </b-btn>
        <b-btn
          id="export-list-cancel"
          class="pl-2"
          variant="link"
          @click="cancel"
        >
          Close
        </b-btn>
      </form>
    </div>
  </div>
</template>

<script>
import FerpaReminder from '@/components/util/FerpaReminder'
import ModalHeader from '@/components/util/ModalHeader'

export default {
  name: 'ExportListModal',
  components: {FerpaReminder, ModalHeader},
  props: {
    cancel: {
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
    export: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    selected: []
  }),
  created() {
    this.selected = this.csvColumnsSelected
  },
  methods: {
    onSubmit() {
      this.export(this.selected)
    }
  }
}
</script>

<style scoped>
.csv-column-options {
  height: 245px;
}
</style>
