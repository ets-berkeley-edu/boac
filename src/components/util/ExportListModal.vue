<template>
  <v-overlay
    v-model="showModalProxy"
    class="justify-center overflow-auto"
    persistent
    scroll-strategy="reposition"
    width="100%"
    @update:model-value="onToggle"
  >
    <v-card
      class="modal-content"
      min-width="500"
      max-width="600"
    >
      <div class="pr-6 pl-6">
        <ModalHeader text="Export List" />
        <hr />
        <div id="export-list-body" class="px-4 py-2">
          <div
            id="csv-column-options"
            aria-label="Select columns to export"
            class="d-flex flex-column flex-wrap csv-column-options mb-5"
            name="csv-column-options"
            role="group"
          >
            <template v-for="(option, index) in csvColumns" :key="index">
              <v-checkbox
                :id="`csv-column-options-${index}`"
                :model-value="includes(selected, option.value)"
                :aria-label="`${option.text} column included in export`"
                class="csv-column-option"
                color="primary"
                density="compact"
                :disabled="isExporting"
                hide-details
                :label="option.text"
                @update:model-value="isChecked => onChange(option.value, isChecked)"
              />
            </template>
          </div>
          <div>
            <span class="font-weight-bold">Reminder:</span> <FerpaReminder />
          </div>
        </div>
        <hr />
        <div aria-live="polite">
          <v-alert
            v-if="error && !isExporting"
            class="font-size-15 mx-4 mb-2"
            color="error"
            density="compact"
            :icon="mdiAlert"
            :text="error"
            title="Error"
            variant="tonal"
          />
        </div>
        <div class="d-flex justify-end px-4 py-2">
          <ProgressButton
            id="export-list-confirm"
            :action="onSubmit"
            :disabled="!selected.length"
            :in-progress="isExporting"
            text="Export"
          />
          <v-btn
            id="export-list-cancel"
            class="ml-1"
            text="Close"
            variant="plain"
            @click="cancel"
          />
        </div>
      </div>
    </v-card>
  </v-overlay>
</template>

<script setup>
import {includes} from 'lodash'
import {mdiAlert} from '@mdi/js'
</script>

<script>
import FerpaReminder from '@/components/util/FerpaReminder'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick} from '@/lib/utils'

export default {
  name: 'ExportListModal',
  components: {FerpaReminder, ModalHeader, ProgressButton},
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
      required: true,
      type: Array
    },
    error: {
      default: undefined,
      type: String,
      required: false
    },
    export: {
      required: true,
      type: Function
    },
    showModal: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    isExporting: false,
    selected: []
  }),
  computed: {
    showModalProxy: {
      get() {
        return this.showModal
      }
    }
  },
  created() {
    this.selected = this.csvColumnsSelected
  },
  methods: {
    onChange(value, isChecked) {
      if (isChecked) {
        this.selected.push(value)
      } else {
        this.selected.splice(this.selected.indexOf(value), 1)
      }
    },
    onSubmit() {
      this.isExporting = true
      this.export(this.selected).then(() => this.isExporting = false)

    },
    onToggle(isOpen) {
      if (isOpen) {
        putFocusNextTick('modal-header')
      } else {
        this.cancel()
      }
    }
  }
}
</script>

<style scoped>
.csv-column-options {
  height: 300px;
}
.csv-column-option {
  height: 30px;
}
</style>
