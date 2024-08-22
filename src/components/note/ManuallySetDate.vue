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
      <v-date-input
        id="manually-set-date-input"
        aria-labelledby="manually-set-date-label"
        autocomplete="off"
        bg-color="white"
        :class="{'rounded-e-0': model.setDate}"
        clearable
        density="compact"
        :disabled="isSaving || boaSessionExpired"
        hide-actions
        hide-details
        :max="new Date()"
        :model-value="model.setDate ? DateTime.fromFormat(model.setDate, 'yyyy-MM-dd').toJSDate() : null"
        placeholder="MM/DD/YYYY"
        prepend-icon=""
        variant="outlined"
        @update:model-value="onUpdateModel"
      />
    </div>
  </div>
</template>

<script setup>
import {DateTime} from 'luxon'
import {storeToRefs} from 'pinia'
import {useNoteStore} from '@/stores/note-edit-session'

const noteStore = useNoteStore()
const {boaSessionExpired, isSaving, model} = storeToRefs(noteStore)

const onUpdateModel = d => {
  const value = d ? DateTime.fromJSDate(d).toFormat('yyyy-MM-dd') : null
  noteStore.setSetDate(value)
}
</script>

<style scoped>
.date-input-container {
  margin-top: 8px;
  max-width: 160px;
}
</style>
