<template>
  <div class="mt-1 mr-3 mb-0 ml-3">
    <div
      v-if="boaSessionExpired"
      id="uh-oh-session-time-out"
      aria-live="polite"
      class="pl-3 pr-3"
      role="alert"
    >
      <SessionExpired />
    </div>
    <div v-if="!boaSessionExpired">
      <div class="d-flex flex-wrap-reverse">
        <div class="flex-grow-1">
          <b-btn
            v-if="mode !== 'editTemplate'"
            id="btn-save-as-template"
            :disabled="isSaving || !$_.trim(model.subject)"
            variant="link"
            @click="saveAsTemplate"
          >
            Save as template
          </b-btn>
        </div>
        <div v-if="mode === 'editTemplate'">
          <b-btn
            id="btn-update-template"
            :disabled="isSaving || !model.subject"
            class="btn-primary-color-override"
            variant="primary"
            @click.prevent="updateTemplate"
          >
            Update Template
          </b-btn>
        </div>
        <div v-if="mode !== 'editTemplate'">
          <b-btn
            id="create-note-button"
            :disabled="isSaving || !completeSidSet.length || !$_.trim(model.subject)"
            class="btn-primary-color-override"
            variant="primary"
            @click.prevent="createNote"
          >
            Save
          </b-btn>
        </div>
        <div>
          <b-btn
            id="create-note-cancel"
            :disabled="isSaving"
            variant="link"
            @click.prevent="cancel"
          >
            Cancel
          </b-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import NoteEditSession from '@/mixins/NoteEditSession'
import SessionExpired from '@/components/note/SessionExpired'
import Util from '@/mixins/Util'

export default {
  name: 'CreateNoteFooter',
  components: {SessionExpired},
  mixins: [Context, NoteEditSession, SessionExpired, Util],
  props: {
    cancel: {
      required: true,
      type: Function
    },
    createNote: {
      required: true,
      type: Function
    },
    saveAsTemplate: {
      required: true,
      type: Function
    },
    updateTemplate: {
      required: true,
      type: Function
    }
  }
}
</script>
