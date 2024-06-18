<template>
  <div>
    <label
      id="manually-set-date-label"
      class="font-size-16 font-weight-700"
      for="manually-set-date-input"
    >
      Manually Set Date
    </label>
    <div class="d-flex mt-2">
      <DatePicker
        v-model="manuallySetDate"
        :max-date="maxDate"
        popover-visibility="focus"
      >
        <template #default="{inputValue, inputEvents}">
          <v-text-field
            id="manually-set-date-input"
            aria-labelledby="manually-set-date-label"
            class="search-input-date"
            :class="{'rounded-e-0': manuallySetDate}"
            density="compact"
            :disabled="isSaving || boaSessionExpired"
            hide-details
            :model-value="inputValue"
            name="manually-set-date-input"
            placeholder="MM/DD/YYYY"
            type="text"
            variant="outlined"
            v-on="inputEvents"
          />
        </template>
      </DatePicker>
      <v-btn
        v-if="manuallySetDate"
        id="manually-set-date-clear"
        class="clear-btn px-0"
        color="btn-secondary"
        :disabled="isSaving || boaSessionExpired"
        variant="flat"
        @click="manuallySetDate = null"
      >
        <v-icon :icon="mdiClose" />
        <span class="sr-only">Clear date</span>
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import {mdiClose} from '@mdi/js'
import {storeToRefs} from 'pinia'
import {useNoteStore} from '@/stores/note-edit-session'

const noteStore = useNoteStore()
const {boaSessionExpired, isSaving, model} = storeToRefs(noteStore)

const maxDate = new Date()
const manuallySetDate = computed({
  get() {
    return model.setDate ? model.setDate.toJSDate() : null
  },
  set(value) {
    noteStore.setSetDate(value)
  }
})
</script>

<style scoped>
.clear-btn {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  height: 40px;
  min-width: 40px;
  width: 40px;
}
.search-input-date {
  max-width: 200px;
}
</style>

<style>
.search-input-date.rounded-e-0 .v-field {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}
</style>
