<template>
  <div v-if="isUndefined(isPrivate)">
    <div id="privacy-permissions-label" class="font-weight-bold mb-1">
      Privacy Permissions
    </div>
    <v-radio-group
      v-model="isPrivate"
      aria-describedby="privacy-permissions-label"
      :disabled="disabled"
      @change="onChange"
    >
      <div>
        <v-radio
          id="note-is-not-private-radio-button"
          :value="false"
        >
          Note available to all advisors
        </v-radio>
      </div>
      <div>
        <v-radio
          id="note-is-private-radio-button"
          :value="true"
        >
          Note available only to CE3
        </v-radio>
      </div>
    </v-radio-group>
  </div>
</template>

<script>
import {isUndefined} from 'lodash'
import {useNoteStore} from '@/stores/note-edit-session'
import {alertScreenReader} from '@/lib/utils'

export default {
  name: 'PrivacyPermissions',
  props: {
    disabled: {
      required: false,
      type: Boolean
    }
  },
  computed: {
    isPrivate: {
      get() {
        return useNoteStore().model.isPrivate
      },
      set(value) {
        useNoteStore().setIsPrivate(value)
      }
    }
  },
  methods: {
    isUndefined,
    onChange() {
      alertScreenReader(this.isPrivate ? 'Available only to CE3' : 'Available to all advisors')
    }
  }
}
</script>
