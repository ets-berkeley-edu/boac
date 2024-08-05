<template>
  <div class="d-flex flex-wrap">
    <div class="flex-grow-1">
      <div class="align-center d-flex">
        <ModalHeader
          header-id="dialog-header-note"
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
    <div id="templates-menu">
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
            :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
            v-bind="props"
          >
            <div class="pr-1">Templates</div>
            <v-icon :icon="mdiMenuDown" size="24" />
          </v-btn>
        </template>
        <v-list v-if="noteStore.noteTemplates.length" variant="flat">
          <v-list-item-action v-for="template in noteStore.noteTemplates" :key="template.id">
            <v-container class="pl-2 pr-4 py-2" fluid>
              <v-row class="d-flex flex-nowrap" no-gutters>
                <v-col cols="8">
                  <v-btn
                    :id="`load-note-template-${template.id}`"
                    class="font-weight-700 d-flex justify-start template-dropdown-title"
                    color="primary"
                    block
                    density="compact"
                    width="400"
                    :text="template.title"
                    variant="text"
                    @click="loadTemplate(template)"
                  />
                </v-col>
                <v-col class="pl-8">
                  <div class="align-center d-flex float-right">
                    <v-dialog v-model="template.isRenameDialogOpen" retain-focus width="auto">
                      <template #activator="{props: activatorProps}">
                        <v-btn
                          v-bind="activatorProps"
                          :id="`btn-rename-note-template-${template.id}`"
                          class="font-size-14"
                          color="primary"
                          density="compact"
                          :disabled="isSaving"
                          size="sm"
                          variant="text"
                          @click="openRenameTemplateDialog(template)"
                        >
                          Rename<span class="sr-only"> template {{ template.title }}</span>
                        </v-btn>
                      </template>
                      <v-card width="600">
                        <v-card-title class="pl-6 pt-5">
                          <ModalHeader header-id="rename-template-dialog-header" text="Rename Your Template" />
                        </v-card-title>
                        <v-card-text class="pr-8 py-2">
                          <v-text-field
                            id="rename-template-input"
                            v-model="updatedTemplateTitle"
                            counter="255"
                            density="compact"
                            :disabled="isSaving"
                            label="Template name"
                            maxlength="255"
                            persistent-counter
                            :rules="[
                              v => !!v || 'Template name is required',
                              v => !v || v.length <= 255 || 'Template name cannot exceed 255 characters.'
                            ]"
                            variant="outlined"
                            @keyup.enter="() => renameTemplate(template)"
                          >
                            <template #counter="{max, value}">
                              <div id="rename-template-counter" aria-live="polite" class="font-size-13 text-no-wrap my-1">
                                <span class="sr-only">Template name has a </span>{{ max }} character limit <span v-if="value">({{ max - value }} left)</span>
                              </div>
                            </template>
                          </v-text-field>
                          <div
                            v-if="error"
                            id="rename-template-error"
                            aria-live="polite"
                            class="text-error font-size-13 font-weight-regular"
                            role="alert"
                          >
                            {{ error }}
                          </div>
                        </v-card-text>
                        <v-card-actions class="pb-6 pr-8">
                          <ProgressButton
                            id="rename-template-confirm"
                            :action="() => renameTemplate(template)"
                            :disabled="isSaving || !size(updatedTemplateTitle) || size(updatedTemplateTitle) > 255"
                            :in-progress="isSaving"
                            :text="isSaving ? 'Renaming' : 'Rename'"
                          />
                          <v-btn
                            id="cancel-rename-template"
                            class="ml-1"
                            :disabled="isSaving"
                            text="Cancel"
                            variant="plain"
                            @click="() => cancel(template)"
                          />
                        </v-card-actions>
                      </v-card>
                    </v-dialog>
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
                      @click="openDeleteTemplateDialog(template)"
                    >
                      Delete<span class="sr-only"> template {{ template.title }}</span>
                    </v-btn>
                    <AreYouSureModal
                      v-model="template.isDeleteDialogOpen"
                      button-label-confirm="Delete"
                      dialog-header="Delete Template"
                      :function-cancel="() => cancel(template)"
                      :function-confirm="() => deleteTemplateConfirmed(template)"
                    >
                      Are you sure you want to delete the <strong>'{{ get(template, 'title') }}'</strong> template?
                    </AreYouSureModal>
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
  </div>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton.vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {applyNoteTemplate} from '@/api/notes'
import {deleteNoteTemplate, renameNoteTemplate} from '@/api/note-templates'
import {disableFocusLock, enableFocusLock} from '@/stores/note-edit-session/utils'
import {get, size} from 'lodash'
import {mdiMenuDown} from '@mdi/js'
import {useNoteStore} from '@/stores/note-edit-session'
import {validateTemplateTitle} from '@/lib/note'
import {ref, watch} from 'vue'

const error = ref('')
const isSaving = ref(false)
const noteStore = useNoteStore()
const updatedTemplateTitle = ref(undefined)
const suppressAutoSaveDraftNoteAlert = ref(false)

watch(() => noteStore.isAutoSavingDraftNote, value => value && setTimeout(() => suppressAutoSaveDraftNoteAlert.value = true, 5000))

const cancel = template => {
  resetTemplate(template, template.title)
  alertScreenReader('Canceled')
  putFocusNextTick('create-note-subject')
  enableFocusLock()
}

const deleteTemplateConfirmed = template => {
  isSaving.value = true
  return deleteNoteTemplate(template.id).then(() => {
    isSaving.value = false
    resetTemplate(template, template.title)
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
  applyNoteTemplate(noteStore.model.id, template.id).then(data => {
    noteStore.setModel(data)
    putFocusNextTick('create-note-subject')
    alertScreenReader(`Template ${data.title} loaded.`)
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

const openDeleteTemplateDialog = template => {
  template.isDeleteDialogOpen = true
  disableFocusLock()
  alertScreenReader('Delete template dialog opened.')
}

const openRenameTemplateDialog = template => {
  updatedTemplateTitle.value = template.title
  template.isRenameDialogOpen = true
  disableFocusLock()
  alertScreenReader('Rename template dialog opened.')
}

const renameTemplate = template => {
  error.value = undefined
  isSaving.value = true
  const errorMessage = validateTemplateTitle({id: template.id, title: updatedTemplateTitle})
  if (errorMessage) {
    error.value = errorMessage
    isSaving.value = false
  } else {
    renameNoteTemplate(template.id, updatedTemplateTitle).then(() => {
      isSaving.value = false
      resetTemplate(template, updatedTemplateTitle)
      alertScreenReader(`Template renamed '${template.title}'.`)
      enableFocusLock()
    })
  }
}

const resetTemplate = (template, title) => {
  template.isDeleteDialogOpen = template.isRenameDialogOpen = false
  template.title = title
  updatedTemplateTitle.value = null
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

<style>
.template-dropdown-title .v-btn__content {
  display: inline-block;
  justify-content: start !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}
</style>
