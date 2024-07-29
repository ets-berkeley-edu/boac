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
        v-model="manuallySetDate"
        aria-labelledby="manually-set-date-label"
        autocomplete="off"
        bg-color="white"
        :class="{'rounded-e-0': manuallySetDate}"
        clearable
        density="compact"
        :disabled="isSaving || boaSessionExpired"
        hide-actions
        hide-details
        :max="new Date()"
        placeholder="MM/DD/YYYY"
        prepend-icon=""
        variant="outlined"
      />
    </div>
  </div>
</template>

<script setup>
import {ref, watch} from 'vue'
import {storeToRefs} from 'pinia'
import {useNoteStore} from '@/stores/note-edit-session'

const noteStore = useNoteStore()
const {boaSessionExpired, isSaving, model} = storeToRefs(noteStore)
const manuallySetDate = ref(model.setDate ? model.setDate : undefined)

watch(manuallySetDate, noteStore.setSetDate)
</script>

<style scoped>
.date-input-container {
  margin-top: 8px;
  max-width: 140px;
}
</style>
