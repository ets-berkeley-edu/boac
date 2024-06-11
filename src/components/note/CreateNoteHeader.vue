<template>
  <div class="d-flex flex-wrap">
    <div class="flex-grow-1">
      <div class="align-center d-flex">
        <ModalHeader
          header-id="modal-header-note"
          :text="{
            createBatch: 'Create Note(s)',
            createNote: 'Create Note',
            editDraft: 'Edit Draft Note',
            editNote: 'Edit Note',
            editTemplate: 'Edit Note Template'
          }[noteStore.mode]"
        />
        <transition
          aria-live="polite"
          name="bounce"
          role="alert"
        >
          <span
            v-if="noteStore.isAutoSavingDraftNote && !suppressAutoSaveDraftNoteAlert"
            class="text-accent-green font-size-12 font-weight-bold mb-1 ml-2"
          >
            DRAFT SAVED
          </span>
        </transition>
      </div>
    </div>
    <div>
      <v-menu
        v-if="noteStore.mode !== 'editTemplate'"
        :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
        location="bottom"
        @update:model-value="onToggleTemplatesMenu"
      >
        <template #activator="{props}">
          <v-btn
            id="my-templates-button"
            class="pr-2"
            color="primary"
            v-bind="props"
          >
            <div class="pr-1">Templates</div>
            <v-icon :icon="mdiMenuDown" size="24" />
          </v-btn>
        </template>
        <v-list v-if="noteStore.noteTemplates.length" variant="flat">
          <v-list-item-action v-for="template in noteStore.noteTemplates" :key="template.id">
            <v-container class="pl-2 pr-4 py-2" fluid>
              <v-row align="center" no-gutters>
                <v-col class="pr-8">
                  <v-btn
                    :id="`load-note-template-${template.id}`"
                    class="font-weight-700 template-dropdown-title text-no-wrap truncate-with-ellipsis"
                    color="primary"
                    density="compact"
                    :text="template.title"
                    variant="text"
                    @click="loadTemplate(template)"
                  />
                </v-col>
                <v-col>
                  <div class="align-center d-flex float-right">
                    <v-btn
                      :id="`btn-rename-note-template-${template.id}`"
                      class="font-size-14"
                      color="primary"
                      density="compact"
                      size="sm"
                      variant="text"
                      @click="() => openRenameTemplateModal(template)"
                    >
                      Rename<span class="sr-only"> template {{ template.title }}</span>
                    </v-btn>
                    <div class="mx-1" role="separator">
                      |
                    </div>
                    <v-btn
                      :id="`btn-edit-note-template-${template.id}`"
                      class="font-size-14"
                      color="primary"
                      density="compact"
                      size="sm"
                      variant="text"
                      @click="editTemplate(template)"
                    >
                      Edit<span class="sr-only"> template {{ template.title }}</span>
                    </v-btn>
                    <div class="mx-1" role="separator">
                      |
                    </div>
                    <v-btn
                      :id="`btn-delete-note-template-${template.id}`"
                      class="font-size-14"
                      color="primary"
                      density="compact"
                      size="sm"
                      variant="text"
                      @click="openDeleteTemplateModal(template)"
                    >
                      Delete<span class="sr-only"> template {{ template.title }}</span>
                    </v-btn>
                  </div>
                </v-col>
              </v-row>
            </v-container>
          </v-list-item-action>
        </v-list>
        <div v-if="!noteStore.noteTemplates.length" id="no-templates-header" class="templates-menu-header text-medium-emphasis">
          <div class="font-weight-bold">Templates</div>
          <div class="templates-menu-instructions">
            You have no saved templates.
          </div>
        </div>
      </v-menu>
    </div>
    <RenameTemplateModal
      v-model="isRenamingTemplate"
      :cancel="cancel"
      :rename="renameTemplate"
      :template="targetTemplate"
      @update:model-value="setRenameTemplateDialog"
    />
    <AreYouSureModal
      v-if="showDeleteTemplateModal"
      :function-cancel="cancel"
      :function-confirm="deleteTemplateConfirmed"
      :show-modal="showDeleteTemplateModal"
      button-label-confirm="Delete"
      modal-header="Delete Template"
    >
      Are you sure you want to delete the <strong>'{{ get(targetTemplate, 'title') }}'</strong> template?
    </AreYouSureModal>
  </div>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import ModalHeader from '@/components/util/ModalHeader'
import RenameTemplateModal from '@/components/note/RenameTemplateModal'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {applyNoteTemplate} from '@/api/notes'
import {deleteNoteTemplate, renameNoteTemplate} from '@/api/note-templates'
import {disableFocusLock, enableFocusLock} from '@/stores/note-edit-session/utils'
import {get, size} from 'lodash'
import {mdiMenuDown} from '@mdi/js'
import {useNoteStore} from '@/stores/note-edit-session'
import {watch} from 'vue'

const noteStore = useNoteStore()
let showDeleteTemplateModal = false
let isRenamingTemplate = false
let suppressAutoSaveDraftNoteAlert = false
let targetTemplate = undefined

watch(() => noteStore.isAutoSavingDraftNote, value => value && setTimeout(() => suppressAutoSaveDraftNoteAlert = true, 5000))

const cancel = () => {
  showDeleteTemplateModal = isRenamingTemplate = false
  targetTemplate = null
  alertScreenReader('Canceled')
  putFocusNextTick('create-note-subject')
  enableFocusLock()
}

const deleteTemplateConfirmed = () => {
  return deleteNoteTemplate(targetTemplate.id).then(() => {
    showDeleteTemplateModal = false
    targetTemplate = null
    alertScreenReader('Template deleted.')
    putFocusNextTick('create-note-subject')
    enableFocusLock()
  })
}

const editTemplate = template => {
  noteStore.setModel(template)
  noteStore.setMode('editTemplate')
  putFocusNextTick('create-note-subject')
  alertScreenReader(`Edit template ${template.title}.`)
}

const loadTemplate = template => {
  applyNoteTemplate(noteStore.model.id, template.id).then(note => {
    noteStore.setModel(note)
    putFocusNextTick('create-note-subject')
    alertScreenReader(`Template ${template.title} loaded.`)
  })
}

const onToggleTemplatesMenu = isOpen => {
  if (isOpen) {
    let count = size(noteStore.noteTemplates)
    const suffix = count === 1 ? 'one saved template' : `${count || 'no'} saved templates`
    alertScreenReader(`Template menu open. You have ${suffix}.`)
  } else {
    alertScreenReader('Templates menu closed.')
  }
}

const openDeleteTemplateModal = template => {
  targetTemplate = template
  disableFocusLock()
  showDeleteTemplateModal = true
  alertScreenReader('Delete template modal opened.')
}
const openRenameTemplateModal = template => {
  targetTemplate = template
  disableFocusLock()
  isRenamingTemplate = true
  alertScreenReader('Rename template modal opened.')
}

const renameTemplate = title => {
  renameNoteTemplate(targetTemplate.id, title).then(() => {
    targetTemplate = null
    isRenamingTemplate = false
    alertScreenReader(`Template renamed '${title}'.`)
    enableFocusLock()
  })
}

const setRenameTemplateDialog = show => {
  isRenamingTemplate = show
  const toggle = show ? disableFocusLock : enableFocusLock
  toggle()
  alertScreenReader(`Dialog ${show ? 'opened' : 'closed'}.`)
}
</script>

<style scoped>
.bounce-enter-active {
  animation: bounce-in 0.75s;
}
.bounce-leave-active {
  animation: bounce-in 0.75s reverse;
}
.templates-menu-header {
  font-size: .875rem;
  padding: 0.5rem 1.5rem;
}
.templates-menu-instructions {
  max-width: 300px;
  white-space: normal;
}
.template-dropdown-title {
  max-width: 200px;
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
</style>
