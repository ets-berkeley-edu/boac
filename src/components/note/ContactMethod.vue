<template>
  <div>
    <label
      id="contact-type-label"
      class="font-weight-bold font-size-14"
      for="contact-type-options"
    >
      Contact Method
    </label>
    <v-radio-group
      id="contact-type-options"
      :model-value="contactType"
      aria-describedby="contact-type-label"
      color="primary"
      density="comfortable"
      :disabled="disabled"
      hide-details
      :ripple="false"
      @change="useContextStore().alertScreenReader(contactType)"
    >
      <v-radio
        id="contact-option-none-radio-button"
        label="None"
        :ripple="false"
        :value="null"
      ></v-radio>
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
</template>

<script>
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

export default {
  name: 'ContactMethod',

  data: () => ({
    contactOptions: [
      'Email',
      'Phone',
      'Online same day',
      'Online scheduled',
      'In-person same day',
      'In person scheduled',
      'Admin'
    ]
  }),
  computed: {
    contactType: {
      get() {
        return useNoteStore().model.contactType
      },
      set(value) {
        useNoteStore().setContactType(value)
      }
    },
    disabled() {
      return !!(useNoteStore().isSaving || useNoteStore().boaSessionExpired)
    }
  },
  methods: {
    useContextStore
  }
}
</script>
