<template>
  <div>
    <label
      id="manually-set-date-label"
      class="font-size-16 font-weight-700"
      for="manually-set-date-input"
    >
      Manually Set Date
    </label>
    <div class="date-input-container">
      <AccessibleDateInput
        aria-label="&quot;set&quot; date"
        container-id="new-note-modal-container"
        :disabled="isSaving || boaSessionExpired"
        :get-value="() => model.setDate ? DateTime.fromFormat(model.setDate, 'yyyy-MM-dd').toJSDate() : null"
        id-prefix="manually-set-date"
        :max-date="new Date()"
        :set-value="updateModel"
      />
    </div>
  </div>
</template>

<script setup>
import AccessibleDateInput from '@/components/util/AccessibleDateInput'
import {DateTime} from 'luxon'
import {storeToRefs} from 'pinia'
import {useNoteStore} from '@/stores/note-edit-session'

const noteStore = useNoteStore()
const {boaSessionExpired, isSaving, model} = storeToRefs(noteStore)

const updateModel = d => {
  const value = d ? DateTime.fromJSDate(d).toFormat('yyyy-MM-dd') : null
  noteStore.setSetDate(value)
}
</script>

<style scoped>
.date-input-container {
  margin-top: 8px;
  max-width: 160px;
  position: relative;
  z-index: 100;
}
</style>
