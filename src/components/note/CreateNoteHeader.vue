<template>
  <v-card-title id="new-note-modal-title" class="d-flex flex-wrap pb-0">
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
        absolute
        attach="#new-note-modal-title"
        :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
        left="100"
        location="bottom"
        max-width="1000"
        no-click-animation
        :width="noteStore.noteTemplates.length ? 1000 : 350"
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
        <v-list
          v-if="noteStore.noteTemplates.length"
          class="scrollbar-gutter-stable"
          variant="flat"
        >
          <v-list-item-action v-for="template in noteStore.noteTemplates" :key="template.id">
            <v-container class="pa-2" fluid>
              <v-row class="align-center d-flex flex-nowrap" no-gutters>
                <v-col cols="8">
                  <v-btn
                    :id="`load-note-template-${template.id}`"
                    class="font-weight-700 d-flex justify-start template-dropdown-title"
                    color="primary"
                    block
                    density="compact"
                    :disabled="isSaving"
                    height="24"
                    :text="template.title"
                    variant="text"
                    width="400"
                    @click="loadTemplate(template)"
                  />
                </v-col>
                <v-col class="pl-8" cols="4">
                  <div class="align-center d-flex justify-end">
                    <v-btn
                      :id="`btn-rename-note-template-${template.id}`"
                      class="min-width-unset font-size-14 px-1"
                      color="primary"
                      density="compact"
                      :disabled="isSaving"
                      height="24"
                      variant="text"
                      @click.stop.prevent="openRenameTemplateDialog(template)"
                    >
                      Rename<span class="sr-only"> template {{ template.title }}</span>
                    </v-btn>
                    <div class="font-weight-light mx-1" role="separator">
                      |
                    </div>
                    <v-btn
                      :id="`btn-edit-note-template-${template.id}`"
                      class="min-width-unset font-size-14 px-1"
                      color="primary"
                      density="compact"
                      :disabled="isSaving"
                      height="24"
                      variant="text"
                      @click="editTemplate(template)"
                    >
                      Edit<span class="sr-only"> template {{ template.title }}</span>
                    </v-btn>
                    <div class="font-weight-light mx-1" role="separator">
                      |
                    </div>
                    <v-btn
                      :id="`btn-delete-note-template-${template.id}`"
                      class="min-width-unset font-size-14 px-1"
                      color="primary"
                      density="compact"
                      :disabled="isSaving"
                      height="24"
                      variant="text"
                      @click.stop="openDeleteTemplateDialog(template)"
                    >
                      Delete<span class="sr-only"> template {{ template.title }}</span>
                    </v-btn>
                  </div>
                </v-col>
              </v-row>
            </v-container>
          </v-list-item-action>
        </v-list>
        <v-list v-if="!noteStore.noteTemplates.length">
          <v-list-item disabled>
            You have no saved templates.
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
    <v-dialog
      v-model="isRenameTemplateDialogOpen"
      :activator="templateToRename ? `btn-rename-note-template-${templateToRename.id}` : null"
      aria-labelledby="rename-template-dialog-header"
      persistent
    >
      <v-card width="600" class="modal-content">
        <FocusLock>
          <v-card-title>
            <ModalHeader header-id="rename-template-dialog-header" text="Rename Your Template" />
          </v-card-title>
          <form @submit.prevent="renameTemplate">
            <v-card-text class="modal-body">
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
          </form>
          <v-card-actions class="modal-footer">
            <ProgressButton
              id="rename-template-confirm"
              :action="renameTemplate"
              :disabled="isSaving || !size(updatedTemplateTitle) || size(updatedTemplateTitle) > 255"
              :in-progress="isSaving"
              :text="isSaving ? 'Renaming' : 'Rename'"
            />
            <v-btn
              id="cancel-rename-template"
              class="ml-2"
              :disabled="isSaving"
              text="Cancel"
              variant="plain"
              @click="() => cancel(templateToRename)"
            />
          </v-card-actions>
        </FocusLock>
      </v-card>
    </v-dialog>
    <AreYouSureModal
      v-model="isDeleteTemplateDialogOpen"
      button-label-confirm="Delete"
      :function-cancel="() => cancel(templateToDelete)"
      :function-confirm="() => deleteTemplateConfirmed()"
      modal-header="Delete Template"
    >
      Are you sure you want to delete the <strong>'{{ get(templateToDelete, 'title') }}'</strong> template?
    </AreYouSureModal>
  </v-card-title>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton.vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {applyNoteTemplate} from '@/api/notes'
import {computed, ref, watch} from 'vue'
import {deleteNoteTemplate, renameNoteTemplate} from '@/api/note-templates'
import {disableFocusLock, enableFocusLock} from '@/stores/note-edit-session/utils'
import {find, get, size, trim} from 'lodash'
import {mdiMenuDown} from '@mdi/js'
import {useNoteStore} from '@/stores/note-edit-session'
import {validateTemplateTitle} from '@/lib/note'

const error = ref('')
const isSaving = ref(false)
const noteStore = useNoteStore()
const updatedTemplateTitle = ref(undefined)
const suppressAutoSaveDraftNoteAlert = ref(false)
const templateToDelete = ref(undefined)
const templateToRename = ref(undefined)

const isDeleteTemplateDialogOpen = computed(() => {
  return !!templateToDelete.value
})

const isRenameTemplateDialogOpen = computed(() => {
  return !!templateToRename.value
})

watch(() => noteStore.isAutoSavingDraftNote, value => value && setTimeout(() => suppressAutoSaveDraftNoteAlert.value = true, 5000))

const cancel = template => {
  resetTemplate(template, template.title)
  alertScreenReader('Canceled')
  putFocusNextTick('my-templates-button')
  enableFocusLock()
}

const deleteTemplateConfirmed = () => {
  isSaving.value = true
  return deleteNoteTemplate(templateToDelete.value.id).then(() => {
    isSaving.value = false
    resetTemplate(templateToDelete.value, templateToDelete.value.title)
    alertScreenReader('Template deleted.')
    putFocusNextTick('my-templates-button')
    enableFocusLock()
  })
}

const editTemplate = template => {
  noteStore.setModel(template)
  noteStore.setMode('editTemplate')
  putFocusNextTick('create-note-subject')
  alertScreenReader(`Editing template ${template.title}.`)
}

const loadTemplate = template => {
  applyNoteTemplate(noteStore.model.id, template.id).then(data => {
    noteStore.setModel(data)
    putFocusNextTick('create-note-subject')
    alertScreenReader(`Template ${template.title} loaded.`)
  })
}

const onToggleTemplatesMenu = isOpen => {
  if (isOpen) {
    let count = size(noteStore.noteTemplates)
    const suffix = count === 1 ? 'one saved template' : `${count || 'no'} saved templates`
    alertScreenReader(`Templates menu open. You have ${suffix}.`)
  } else {
    alertScreenReader('Templates menu closed.')
  }
}

const openDeleteTemplateDialog = template => {
  templateToDelete.value = template
  disableFocusLock()
}

const openRenameTemplateDialog = template => {
  templateToRename.value = template
  updatedTemplateTitle.value = template.title
  disableFocusLock()
  putFocusNextTick('rename-template-input')
}

const renameTemplate = () => {
  const template = find(noteStore.noteTemplates, {'id': templateToRename.value.id})
  const templateTitle = trim(updatedTemplateTitle.value)
  error.value = undefined
  isSaving.value = true
  const errorMessage = validateTemplateTitle({id: template.id, title: templateTitle})
  if (errorMessage) {
    error.value = errorMessage
    isSaving.value = false
  } else {
    alertScreenReader('Renaming template')
    renameNoteTemplate(template.id, templateTitle).then(() => {
      isSaving.value = false
      resetTemplate(template, templateTitle)
      alertScreenReader(`Template renamed '${template.title}'.`)
      putFocusNextTick('my-templates-button')
      enableFocusLock()
    })
  }
}

const resetTemplate = (template, title) => {
  template.title = title
  updatedTemplateTitle.value = null
  templateToDelete.value = null
  templateToRename.value = null
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
