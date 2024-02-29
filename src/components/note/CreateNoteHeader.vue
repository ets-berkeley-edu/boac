<template>
  <div class="d-flex flex-wrap mb-1 mt-2 pt-2">
    <div class="flex-grow-1">
      <div class="align-items-center d-flex">
        <ModalHeader
          class="border-bottom-0"
          header-id="modal-header-note"
          :text="headerText"
        />
        <transition
          aria-live="polite"
          name="bounce"
          role="alert"
        >
          <span
            v-if="isAutoSavingDraftNote && !suppressAutoSaveDraftNoteAlert"
            class="accent-color-green font-size-12 font-weight-700 mb-1 ml-2"
          >
            DRAFT SAVED
          </span>
        </transition>
      </div>
    </div>
    <div class="mr-4">
      <!-- TODO: if v-select is not accessible, we need to find a better replacement for b-dropdown -->
      <!-- <b-dropdown
        v-if="mode !== 'editTemplate'"
        id="my-templates-button"
        class="mb-3 ml-0 pb-1"
        :disabled="isSaving || boaSessionExpired"
        right
        text="Templates"
        toggle-class="btn-primary-color-override"
        variant="primary"
        @show="onShowTemplatesMenu"
        @hide="alertScreenReader('Templates menu closed.')"
      >
        <b-dropdown-header v-if="!_size(noteTemplates)" id="no-templates-header" class="templates-dropdown-header">
          <div class="font-weight-bolder">Templates</div>
          <div class="templates-dropdown-instructions">
            You have no saved templates.
          </div>
        </b-dropdown-header>
        <b-dropdown-text
          v-for="template in noteTemplates"
          :key="template.id"
        >
          <div class="align-items-center d-flex font-weight-normal justify-content-between text-nowrap">
            <v-btn
              :id="`load-note-template-${template.id}`"
              :title="template.title"
              class="pb-0 text-nowrap template-dropdown-title truncate-with-ellipsis"
              variant="link"
              @click="loadTemplate(template)"
            >
              {{ template.title }}
            </v-btn>
            <div class="align-items-center d-flex ml-3">
              <div class="pl-2">
                <v-btn
                  :id="`btn-rename-note-template-${template.id}`"
                  variant="link"
                  class="p-0"
                  @click="openRenameTemplateModal(template)"
                >
                  Rename<span class="sr-only"> template {{ template.title }}</span>
                </v-btn>
              </div>
              <div class="pl-1 pr-1">
                |
              </div>
              <div>
                <v-btn
                  :id="`btn-edit-note-template-${template.id}`"
                  variant="link"
                  class="p-0"
                  @click="editTemplate(template)"
                >
                  Edit<span class="sr-only"> template {{ template.title }}</span>
                </v-btn>
              </div>
              <div class="pl-1 pr-1">
                |
              </div>
              <div>
                <v-btn
                  :id="`btn-delete-note-template-${template.id}`"
                  variant="link"
                  class="p-0"
                  @click="openDeleteTemplateModal(template)"
                >
                  Delete<span class="sr-only"> template {{ template.title }}</span>
                </v-btn>
              </div>
            </div>
          </div>
        </b-dropdown-text>
      </b-dropdown> -->
    </div>
    <RenameTemplateModal
      v-if="showRenameTemplateModal"
      :show-modal="showRenameTemplateModal"
      :cancel="cancel"
      :rename="renameTemplate"
      :template="targetTemplate"
      :toggle-show="toggleShowRenameTemplateModal"
    />
    <AreYouSureModal
      v-if="showDeleteTemplateModal"
      :function-cancel="cancel"
      :function-confirm="deleteTemplateConfirmed"
      :modal-body="`Are you sure you want to delete the <b>'${_get(targetTemplate, 'title')}'</b> template?`"
      :show-modal="showDeleteTemplateModal"
      button-label-confirm="Delete"
      modal-header="Delete Template"
    />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Context from '@/mixins/Context'
import ModalHeader from '@/components/util/ModalHeader'
import NoteEditSession from '@/mixins/NoteEditSession'
import RenameTemplateModal from '@/components/note/RenameTemplateModal'
import Util from '@/mixins/Util'
import {applyNoteTemplate} from '@/api/notes'
import {deleteNoteTemplate, renameNoteTemplate} from '@/api/note-templates'

export default {
  name: 'CreateNoteHeader',
  components: {AreYouSureModal, ModalHeader, RenameTemplateModal},
  mixins: [Context, NoteEditSession, Util],
  props: {
    cancelPrimaryModal: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    modalHeader: undefined,
    showDeleteTemplateModal: false,
    showRenameTemplateModal: false,
    suppressAutoSaveDraftNoteAlert: false,
    targetTemplate: undefined
  }),
  computed: {
    headerText() {
      let text
      switch (this.mode) {
      case 'createBatch':
        text = 'Create Note(s)'
        break
      case 'createNote':
        text = 'Create Note'
        break
      case 'editDraft':
        text = 'Edit Draft Note'
        break
      case 'editNote':
        text = 'Edit Note'
        break
      case 'editTemplate':
        text = 'Edit Note Template'
        break
      }
      return text
    }
  },
  watch: {
    isAutoSavingDraftNote(value) {
      if (value) {
        setTimeout(() => {
          this.suppressAutoSaveDraftNoteAlert = true
        }, 5000)
      }
    }
  },
  methods: {
    cancel() {
      this.showDeleteTemplateModal = false
      this.showRenameTemplateModal = false
      this.targetTemplate = null
      this.alertScreenReader('Canceled')
      this.putFocusNextTick('create-note-subject')
      this.enableFocusLock()
    },
    deleteTemplateConfirmed() {
      return deleteNoteTemplate(this.targetTemplate.id).then(() => {
        this.showDeleteTemplateModal = false
        this.targetTemplate = null
        this.alertScreenReader('Template deleted.')
        this.putFocusNextTick('create-note-subject')
        this.enableFocusLock()
      })
    },
    editTemplate(template) {
      this.setModel(template)
      this.setMode('editTemplate')
      this.putFocusNextTick('create-note-subject')
      this.alertScreenReader(`Edit template ${template.title}.`)
    },
    loadTemplate(template) {
      applyNoteTemplate(this.model.id, template.id).then(note => {
        this.setModel(note)
        this.putFocusNextTick('create-note-subject')
        this.alertScreenReader(`Template ${template.title} loaded.`)
      })
    },
    onShowTemplatesMenu() {
      let count = this._size(this.noteTemplates)
      const suffix = count === 1 ? 'one saved template' : `${count || 'no'} saved templates`
      this.alertScreenReader(`Template menu open. You have ${suffix}.`)
    },
    openDeleteTemplateModal(template) {
      this.targetTemplate = template
      this.disableFocusLock()
      this.showDeleteTemplateModal = true
      this.alertScreenReader('Delete template modal opened.')
    },
    openRenameTemplateModal(template) {
      this.targetTemplate = template
      this.disableFocusLock()
      this.showRenameTemplateModal = true
      this.alertScreenReader('Rename template modal opened.')
    },
    renameTemplate(title) {
      renameNoteTemplate(this.targetTemplate.id, title).then(() => {
        this.targetTemplate = null
        this.showRenameTemplateModal = false
        this.alertScreenReader(`Template renamed '${title}'.`)
        this.enableFocusLock()
      })
    },
    toggleShowRenameTemplateModal(show) {
      this.showRenameTemplateModal = show
      const toggle = show ? this.disableFocusLock : this.enableFocusLock
      toggle()
      this.alertScreenReader(`Dialog ${show ? 'opened' : 'closed'}.`)
    }
  }
}
</script>

<style scoped>
.bounce-enter-active {
  animation: bounce-in 0.75s;
}
.bounce-leave-active {
  animation: bounce-in 0.75s reverse;
}
@keyframes bounce-in {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.25);
  }
  100% {
    transform: scale(1);
  }
}
.template-dropdown-title {
  max-width: 200px;
}
.templates-dropdown-header {
  width: 300px;
}
.templates-dropdown-instructions {
  max-width: 300px;
  white-space: normal;
}
</style>
