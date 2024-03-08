<template>
  <div class="pt-1 px-3 pb-0">
    <div
      v-if="boaSessionExpired"
      id="uh-oh-session-time-out"
      aria-live="polite"
      class="pl-3 pr-3"
      role="alert"
    >
      <SessionExpired />
    </div>
    <div v-if="!boaSessionExpired" class="d-flex flex-wrap">
      <div class="flex-grow-1">
        <v-btn
          v-if="!['editTemplate'].includes(mode)"
          id="btn-save-as-template"
          color="primary"
          :disabled="isSaving || !_trim(model.subject) || !!model.setDate || !!model.contactType"
          variant="text"
          @click="saveAsTemplate"
        >
          Save as template
        </v-btn>
      </div>
      <div class="d-flex">
        <div v-if="mode === 'editTemplate'">
          <v-btn
            id="btn-update-template"
            class="mr-1"
            color="primary"
            :disabled="isSaving || !model.subject"
            @click.prevent="updateTemplate"
          >
            Update Template
          </v-btn>
        </div>
        <div v-if="model.isDraft">
          <v-btn
            id="save-as-draft-button"
            class="mr-1"
            color="primary"
            :disabled="isSaving || (!_trim(model.subject) && !_trim(model.body))"
            variant="text"
            @click.prevent="updateNote"
          >
            Save and Close Draft
          </v-btn>
        </div>
        <div v-if="!['editTemplate'].includes(mode)">
          <v-btn
            id="create-note-button"
            :class="{'mr-2': mode !== 'editDraft'}"
            color="primary"
            :disabled="isSaving || !completeSidSet.length || !_trim(model.subject)"
            @click.prevent="publish"
          >
            Publish Note
          </v-btn>
        </div>
        <div v-if="mode !== 'editDraft'">
          <v-btn
            id="create-note-cancel"
            color="error"
            :disabled="isSaving"
            variant="outlined"
            @click.prevent="cancel"
          >
            Discard
          </v-btn>
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
    saveAsTemplate: {
      required: true,
      type: Function
    },
    updateNote: {
      required: true,
      type: Function
    },
    updateTemplate: {
      required: true,
      type: Function
    }
  },
  methods: {
    publish() {
      this.setIsDraft(false)
      this.updateNote()
    }
  }
}
</script>
