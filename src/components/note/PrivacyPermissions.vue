<template>
  <div v-if="!_isUndefined(isPrivate)">
    <div id="privacy-permissions-label" class="font-weight-bold mb-1">
      Privacy Permissions
    </div>
    <b-form-radio-group
      v-model="isPrivate"
      aria-describedby="privacy-permissions-label"
      :disabled="disabled"
      @change="$announcer.polite(isPrivate ? 'Available only to CE3' : 'Available to all advisors')"
    >
      <div>
        <b-form-radio
          id="note-is-not-private-radio-button"
          :value="false"
        >
          Note available to all advisors
        </b-form-radio>
      </div>
      <div>
        <b-form-radio
          id="note-is-private-radio-button"
          :value="true"
        >
          Note available only to CE3
        </b-form-radio>
      </div>
    </b-form-radio-group>
  </div>
</template>

<script>
import NoteEditSession from '@/mixins/NoteEditSession'
import Util from '@/mixins/Util'

export default {
  name: 'PrivacyPermissions',
  mixins: [NoteEditSession, Util],
  props: {
    disabled: {
      required: false,
      type: Boolean
    }
  },
  computed: {
    isPrivate: {
      get() {
        return this.model.isPrivate
      },
      set(value) {
        this.setIsPrivate(value)
      }
    }
  }
}
</script>
