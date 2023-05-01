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
            v-if="!['editTemplate'].includes(mode)"
            id="btn-save-as-template"
            :disabled="isSaving || !$_.trim(model.subject) || !!model.setDate || !!model.contactType"
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
        <div v-if="model.isDraft">
          <b-btn
            id="save-as-draft-button"
            class="mr-1"
            :disabled="isSaving || (!$_.trim(model.subject) && !$_.trim(model.body))"
            variant="link"
            @click.prevent="updateNote"
          >
            Save and Close Draft
          </b-btn>
        </div>
        <div v-if="!['editTemplate'].includes(mode)">
          <b-btn
            id="create-note-button"
            :disabled="isSaving || !completeSidSet.length || !$_.trim(model.subject)"
            class="btn-primary-color-override"
            :class="{'mr-2': mode !== 'editDraft'}"
            variant="primary"
            @click.prevent="publish"
          >
            Publish Note
          </b-btn>
        </div>
        <div v-if="mode !== 'editDraft'">
          <b-btn
            id="create-note-cancel"
            class="has-error"
            :disabled="isSaving"
            variant="outline-danger"
            @click.prevent="cancel"
          >
            Discard
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
