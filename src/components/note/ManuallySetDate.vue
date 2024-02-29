<template>
  <div>
    <div id="manually-set-date-label" class="font-weight-bold mb-1">
      Manually Set Date
    </div>
    <div class="d-flex w-100">
      <v-date-picker
        v-model="manuallySetDate"
        :max-date="maxDate"
        popover-visibility="focus"
      >
        <template #default="{inputValue, inputEvents}">
          <input
            id="manually-set-date-input"
            aria-labelledby="manually-set-date-label"
            class="search-input-date form-control"
            name="manually-set-date-input"
            placeholder="MM/DD/YYYY"
            type="text"
            :value="inputValue"
            v-on="inputEvents"
          />
        </template>
      </v-date-picker>
      <div v-if="manuallySetDate">
        <v-btn
          id="manually-set-date-clear"
          class="search-input-date"
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
import {mdiClose} from '@mdi/js'
</script>

<script>
import NoteEditSession from '@/mixins/NoteEditSession'

export default {
  name: 'ManuallySetDate',
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
.search-input-date {
  margin-bottom: 10px;
}
</style>
