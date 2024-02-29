<template>
  <div>
    <div id="manually-set-date-label" class="font-weight-bold mb-1">
      Manually Set Date
    </div>
    <div class="d-flex w-100">
      <div class="w-50">
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
              density="compact"
              hide-details
              :model-value="inputValue"
              name="manually-set-date-input"
              placeholder="MM/DD/YYYY"
              type="text"
              variant="outlined"
              v-on="inputEvents"
            ></v-text-field>
          </template>
        </DatePicker>
      </div>
      <div>
        <v-btn
          v-if="manuallySetDate"
          id="manually-set-date-clear"
          class="clear-btn px-0"
          color="btn-secondary"
          variant="flat"
          @click="manuallySetDate = null"
        >
          <v-icon :icon="mdiClose" />
          <span class="sr-only">Clear date</span>
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script setup>
import {DatePicker} from 'v-calendar'
import {mdiClose} from '@mdi/js'
</script>

<script>
import NoteEditSession from '@/mixins/NoteEditSession'

export default {
  name: 'ManuallySetDate',
  components: {DatePicker},
  mixins: [NoteEditSession],
  props: {
    disabled: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    maxDate: new Date()
  }),
  computed: {
    manuallySetDate: {
      get() {
        return this.model.setDate ? this.model.setDate.toDate() : null
      },
      set(value) {
        this.setSetDate(value)
      }
    }
  }
}
</script>

<style scoped>
.clear-btn {
  height: 40px;
  min-width: 40px;
  width: 40px;
}
</style>
