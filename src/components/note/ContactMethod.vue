<template>
  <div>
    <div id="contact-type-label" class="font-weight-bold mb-1">
      Contact Method
    </div>
    <b-form-radio-group
      id="contact-type-options"
      v-model="contactType"
      aria-describedby="contact-type-label"
      :disabled="disabled"
      @change="$announcer.polite(contactType)"
    >
      <b-form-radio id="contact-option-none-radio-button" :value="null">
        None
      </b-form-radio>
      <div v-for="(contactOption, index) in contactOptions" :key="contactOption">
        <b-form-radio
          :id="`contact-option-${index}-radio-button`"
          :value="contactOption"
        >
          {{ contactOption }}
        </b-form-radio>
      </div>
    </b-form-radio-group>
  </div>
</template>

<script>
import NoteEditSession from '@/mixins/NoteEditSession'

export default {
  name: 'ContactMethod',
  mixins: [NoteEditSession],
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
