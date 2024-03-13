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
      v-model="contactType"
      aria-describedby="contact-type-label"
      color="primary"
      density="comfortable"
      :disabled="disabled"
      hide-details
      :ripple="false"
      @change="alertScreenReader(contactType)"
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
import Context from '@/mixins/Context'
import NoteEditSession from '@/mixins/NoteEditSession'

export default {
  name: 'ContactMethod',
  mixins: [Context, NoteEditSession],
  props: {
    disabled: {
      required: false,
      type: Boolean
    }
  },
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
        return this.model.contactType
      },
      set(value) {
        this.setContactType(value)
      }
    }
  }
}
</script>
