<template>
  <div>
    <label
      id="contact-type-label"
      class="font-size-16 font-weight-700"
      for="contact-type-options"
    >
      Contact Method
    </label>
    <div class="mt-1">
      <v-radio-group
        id="contact-type-options"
        aria-describedby="contact-type-label"
        color="primary"
        density="compact"
        :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
        hide-details
        :model-value="noteStore.model.contactType"
        :ripple="false"
        @update:model-value="onChangeContactType"
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
          />
        </template>
      </v-radio-group>
    </div>
  </div>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {useNoteStore} from '@/stores/note-edit-session'

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

const onChangeContactType = value => {
  alertScreenReader(value)
  noteStore.setContactType(value)
}
</script>
