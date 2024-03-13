<template>
  <div class="d-flex flex-wrap">
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
            class="text-accent-green font-size-12 font-weight-bold mb-1 ml-2"
          >
            DRAFT SAVED
          </span>
        </transition>
      </div>
    </div>
    <div class="mr-4">
      <v-select
        v-if="mode !== 'editTemplate'"
        id="my-templates-button"
        v-model="selectedTemplate"
        bg-color="primary"
        class="templates-dropdown"
        density="compact"
        :disabled="isSaving || boaSessionExpired"
        hide-details
        item-value="id"
        :items="noteTemplates"
        label="Templates"
        :menu-props="{contentClass: 'bg-white', location: 'bottom right'}"
        persistent-hint
        return-object
        single-line
        variant="solo-filled"
        @update:menu="onToggleTemplatesMenu"
      >
        <template #no-data>
          <div id="no-templates-header" class="templates-dropdown-header text-medium-emphasis">
            <div class="font-weight-bold">Templates</div>
            <div class="templates-dropdown-instructions">
              You have no saved templates.
            </div>
          </div>
        </template>
        <template #item="{props, item}">
          <v-list-item v-bind="props">
            <template #title="{title}">
              <v-btn
                :id="`load-note-template-${item.raw.id}`"
                :title="title"
                class="text-nowrap template-dropdown-title truncate-with-ellipsis"
                color="primary"
                density="compact"
                variant="text"
                @click="loadTemplate(item.raw)"
              >
                {{ title }}
              </v-btn>
            </template>
            <template #append>
              <v-list-item-action end>
                <div class="align-items-center d-flex ml-3">
                  <div class="pl-2">
                    <v-btn
                      :id="`btn-rename-note-template-${item.raw.id}`"
                      class="px-2"
                      density="compact"
                      variant="text"
                      @click="openRenameTemplateModal(item.raw)"
                    >
                      Rename<span class="sr-only"> template {{ item.raw.title }}</span>
                    </v-btn>
                  </div>
                  <div aria-role="separator">
                    |
                  </div>
                  <div>
                    <v-btn
                      :id="`btn-edit-note-template-${item.raw.id}`"
                      class="px-2"
                      density="compact"
                      variant="text"
                      @click="editTemplate(item.raw)"
                    >
                      Edit<span class="sr-only"> template {{ item.raw.title }}</span>
                    </v-btn>
                  </div>
                  <div aria-role="separator">
                    |
                  </div>
                  <div>
                    <v-btn
                      :id="`btn-delete-note-template-${item.raw.id}`"
                      class="px-2"
                      density="compact"
                      variant="text"
                      @click="openDeleteTemplateModal(item.raw)"
                    >
                      Delete<span class="sr-only"> template {{ item.raw.title }}</span>
                    </v-btn>
                  </div>
                </div>
              </v-list-item-action>
            </template>
          </v-list-item>
        </template>
      </v-select>
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
      :show-modal="showDeleteTemplateModal"
      button-label-confirm="Delete"
      modal-header="Delete Template"
    >
      Are you sure you want to delete the <strong>'{{ _get(targetTemplate, 'title') }}'</strong> template?
    </AreYouSureModal>
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
    selectedTemplate: undefined,
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
    onToggleTemplatesMenu(isOpen) {
      if (isOpen) {
        let count = this._size(this.noteTemplates)
        const suffix = count === 1 ? 'one saved template' : `${count || 'no'} saved templates`
        this.alertScreenReader(`Template menu open. You have ${suffix}.`)
      } else {
        this.alertScreenReader('Templates menu closed.')
      }
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

<style>
.template-dropdown-title {
  max-width: 200px;
}
.templates-dropdown-header {
  font-size: .875rem;
  padding: 0.5rem 1.5rem;
}
.templates-dropdown-instructions {
  max-width: 300px;
  white-space: normal;
}
</style>

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
.templates-dropdown {
  width: 170px;
}
</style>
