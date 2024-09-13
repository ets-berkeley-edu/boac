<template>
  <v-dialog
    v-model="showModalProxy"
    aria-describedby="export-list-body"
    aria-labelledby="modal-header"
    persistent
    scroll-strategy="reposition"
    width="100%"
  >
    <v-card
      class="modal-content"
      min-width="500"
      max-width="800"
    >
      <FocusLock @keydown.esc="cancel">
        <v-card-title>
          <ModalHeader text="Export List" />
        </v-card-title>
        <v-card-text id="export-list-body" class="modal-body">
          <div
            id="csv-column-options"
            aria-label="Select columns to export"
            class="d-flex flex-column flex-wrap csv-column-options pb-5 px-1"
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
        </v-card-text>
        <hr />
        <v-card-actions class="modal-footer flex-column">
          <v-alert
            v-if="error && !isExporting"
            aria-live="polite"
            class="font-size-15 w-100 mb-3"
            color="error"
            density="compact"
            :icon="mdiAlert"
            :text="error"
            title="Error"
            variant="tonal"
          />
          <div class="d-flex justify-end w-100">
            <ProgressButton
              id="export-list-confirm"
              :action="onSubmit"
              :disabled="!selected.length || error || isExporting"
              :in-progress="isExporting"
              :text="isExporting ? 'Exporting' : 'Export'"
            />
            <v-btn
              id="export-list-cancel"
              class="ml-2"
              :disabled="isExporting"
              text="Close"
              variant="text"
              @click="cancel"
            />
          </div>
        </v-card-actions>
      </FocusLock>
    </v-card>
  </v-dialog>
</template>

<script setup>
import FerpaReminder from '@/components/util/FerpaReminder'
import FocusLock from 'vue-focus-lock'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {computed, ref} from 'vue'
import {includes} from 'lodash'
import {mdiAlert} from '@mdi/js'

const props = defineProps({
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
})

const isExporting = ref(false)
const selected = ref(props.csvColumnsSelected)
const showModalProxy = computed(() => {
  return props.showModal
})

const onChange = (value, isChecked) => {
  if (isChecked) {
    selected.value.push(value)
  } else {
    selected.value.splice(selected.value.indexOf(value), 1)
  }
}

const onSubmit = () => {
  isExporting.value = true
  this.export(selected.value).then(() => isExporting.value = false)

}
</script>

<style scoped>
.csv-column-options {
  height: 320px;
}
.csv-column-option {
  height: 30px;
}
</style>
