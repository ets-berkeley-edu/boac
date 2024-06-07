<template>
  <div>
    <label
      id="contact-type-label"
      class="font-size-16 font-weight-700"
      for="contact-type-options"
    >
      Contact Method
    </label>
    <div class="mt-2">
      <v-radio-group
        id="contact-type-options"
        aria-describedby="contact-type-label"
        color="primary"
        density="compact"
        :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
        hide-details
        :model-value="contactType"
        :ripple="false"
        @change="alertScreenReader(contactType)"
      >
        <v-radio
          id="contact-option-none-radio-button"
          label="None"
          :ripple="false"
          :value="null"
        />
        <template v-for="(contactOption, index) in contactOptions" :key="contactOption">
          <v-radio
            :id="`contact-option-${index}-radio-button`"
            :label="contactOption"
            :ripple="false"
            :value="contactOption"
          >
          </v-radio>
        </template>
      </v-radio-group>
    </div>
  </div>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {useNoteStore} from '@/stores/note-edit-session'
import {computed} from 'vue'

const noteStore = useNoteStore()
const contactOptions = [
  'Email',
  'Phone',
  'Online same day',
  'Online scheduled',
  'In-person same day',
  'In person scheduled',
  'Admin'
]
const contactType = computed({
  get() {
    return noteStore.model.contactType
  },
  set(value) {
    noteStore.setContactType(value)
  }
})
</script>
