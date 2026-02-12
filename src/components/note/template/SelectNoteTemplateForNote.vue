<template>
  <div>
    <div>
      <v-menu
        v-if="noteStore.mode !== 'editTemplate'"
        id="templates-menu"
        absolute
        attach="#edit-note-header"
        :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
        left="100"
        location="bottom"
        max-width="1000"
        no-click-animation
        :width="noteStore.noteTemplates.length ? 1000 : 350"
        @update:model-value="onToggleTemplatesMenu"
      >
        <template #activator="{props: menuProps}">
          <v-btn
            id="my-templates-button"
            class="ml-auto mb-3"
            color="primary"
            :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
            flat
            v-bind="menuProps"
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
          <v-list-item
            v-for="template in noteStore.noteTemplates"
            :key="template.id"
            class="pa-0"
            :active="size(noteStore.noteTemplates) > 1 && template.id === activeTemplateId"
          >
            <v-container class="pl-0 py-2" fluid>
              <v-row class="align-center d-flex" no-gutters>
                <v-col class="template-name py-0" cols="12" md="8">
                  <button
                    :id="`load-note-template-${template.id}`"
                    :aria-label="`Use template &quot;${template.title}&quot;`"
                    class="v-btn d-flex font-size-15 font-weight-550 load-note-template-btn justify-start ml-2 pl-2 text-primary text-capitalize w-100"
                    :disabled="isSaving"
                    :title="template.title"
                    @click="loadTemplate(template)"
                    @focus="activeTemplateId = template.id"
                  >
                    <span class="v-btn__overlay" />
                    <div class="truncate-with-ellipsis">{{ template.title }}</div>
                  </button>
                </v-col>
                <v-col class="template-actions pl-8 pr-3" cols="12" md="4">
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
                      @focus="activeTemplateId = template.id"
                    >
                      Rename<span class="sr-only"> template &quot;{{ template.title }}&quot;</span>
                    </v-btn>
                    <div class="font-weight-light mb-1 mx-1 text-medium-emphasis" role="separator">
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
                      @focus="activeTemplateId = template.id"
                    >
                      Edit<span class="sr-only"> template &quot;{{ template.title }}&quot;</span>
                    </v-btn>
                    <div class="font-weight-light mb-1 mx-1 text-medium-emphasis" role="separator">
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
                      @focus="activeTemplateId = template.id"
                    >
                      Delete<span class="sr-only"> template &quot;{{ template.title }}&quot;</span>
                    </v-btn>
                  </div>
                </v-col>
              </v-row>
            </v-container>
          </v-list-item>
        </v-list>
        <v-list v-if="!noteStore.noteTemplates.length">
          <v-list-item disabled>
            <span class="font-size-16 font-weight-medium">You have no saved templates.</span>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
    <v-dialog
      v-model="isRenameTemplateDialogOpen"
      :activator="templateToRename ? `btn-rename-note-template-${templateToRename.id}` : undefined"
      aria-labelledby="rename-template-dialog-header"
      persistent
    >
      <v-card width="600" class="modal-content">
        <FocusLock>
          <v-card-title>
            <ModalHeader header-id="rename-template-dialog-header" text="Rename Your Template" />
          </v-card-title>
          <v-card-text class="modal-body">
            <v-text-field
              id="rename-template-input"
              v-model="updatedTemplateTitle"
              aria-describedby="rename-template-input-details"
              :aria-invalid="!!error"
              autocomplete="on"
              counter="255"
              :disabled="isSaving"
              :error="!!error"
              :error-messages="error"
              label="Template name"
              maxlength="255"
              persistent-counter
              required
              :rules="[
                v => !!trim(v) || 'Template name is required',
                v => !v || trim(v).length <= 255 || 'Template name cannot exceed 255 characters.'
              ]"
              validate-on="lazy invalid-input"
            >
              <template #counter="{max, value}">
                <CharacterCount
                  v-if="max"
                  :count="toInt(value || 0)"
                  id-prefix="rename-template"
                  :max="toInt(max)"
                />
              </template>
              <template #message="{message}">
                <v-alert
                  id="rename-template-error"
                  class="font-size-14 line-height-normal"
                  density="compact"
                  role="none"
                  :text="message"
                  type="error"
                  variant="tonal"
                />
              </template>
            </v-text-field>
          </v-card-text>
          <v-card-actions class="modal-footer">
            <ProgressButton
              id="rename-template-confirm"
              aria-label="Rename Template"
              :action="renameTemplate"
              :disabled="isSaving || !size(updatedTemplateTitle) || size(updatedTemplateTitle) > 255"
              :in-progress="isSaving"
              :text="isSaving ? 'Renaming' : 'Rename'"
            />
            <v-btn
              id="cancel-rename-template"
              aria-label="Cancel Rename Template"
              class="ml-2"
              :disabled="isSaving"
              text="Cancel"
              variant="text"
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
      :function-confirm="deleteTemplateConfirmed"
      modal-header="Delete Template"
    >
      Are you sure you want to delete the <strong>'{{ get(templateToDelete, 'title') }}'</strong> template?
    </AreYouSureModal>
  </div>
</template>

<script setup lang="ts">
import FocusLock from 'vue-focus-lock'
import {computed, ref, watch} from 'vue'
import {find, get, isUndefined, size, trim} from 'lodash'
import {mdiMenuDown} from '@mdi/js'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import CharacterCount from '@/components/util/CharacterCount.vue'
import ModalHeader from '@/components/util/ModalHeader.vue'
import ProgressButton from '@/components/util/ProgressButton.vue'
import type {NoteTemplate} from '@/lib/types'
import {alertScreenReader, putFocusNextTick, toInt} from '@/lib/utils'
import {applyNoteTemplate} from '@/api/notes'
import {deleteNoteTemplate, renameNoteTemplate} from '@/api/note-templates'
import {disableFocusLock, enableFocusLock} from '@/stores/note-edit-session/note-edit-session-utils'
import {useNoteStore} from '@/stores/note-edit-session'
import {validateTemplateTitle} from '@/lib/note'

const activeTemplateId = ref()
const error = ref<string | undefined>()
const isSaving = ref(false)
const templateToDelete = ref<NoteTemplate | undefined>(undefined)
const templateToRename = ref<NoteTemplate | undefined>(undefined)
const updatedTemplateTitle = ref<string | undefined>(undefined)

const noteStore = useNoteStore()

const isDeleteTemplateDialogOpen = computed(() => {
  return !!templateToDelete.value
})

const isRenameTemplateDialogOpen = computed(() => {
  return !!templateToRename.value
})

watch(updatedTemplateTitle, () => {
  error.value = ''
})

const cancel = template => {
  resetTemplate(template, template.title)
  alertScreenReader('Canceled')
  putFocusNextTick('my-templates-button')
  enableFocusLock()
}

const deleteTemplateConfirmed = () => {
  isSaving.value = true
  if (isUndefined(templateToDelete.value)) {
    isSaving.value = false
  } else {
    const title = templateToDelete.value.title
    deleteNoteTemplate(templateToDelete.value.id).then(() => {
      isSaving.value = false
      alertScreenReader(`Deleted template ${title}`)
      resetTemplate(templateToDelete.value, title)
      putFocusNextTick('my-templates-button')
      enableFocusLock()
    })
  }
}

const editTemplate = template => {
  noteStore.setModel(template)
  noteStore.setMode('editTemplate')
  putFocusNextTick('create-note-subject')
}

const loadTemplate = template => {
  applyNoteTemplate(noteStore.model.id, template.id).then(data => {
    noteStore.setModel(data)
    alertScreenReader(`Using template ${template.title}.`)
    putFocusNextTick('create-note-subject')
  })
}

const onToggleTemplatesMenu = isOpen => {
  if (isOpen) {
    const count = size(noteStore.noteTemplates)
    const suffix = count === 1 ? 'one saved template' : `${count || 'no'} saved templates`
    alertScreenReader(`You have ${suffix}.`)
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
  if (templateToRename.value) {
    const template = find(noteStore.noteTemplates, {'id': templateToRename.value.id})
    const templateTitle = trim(updatedTemplateTitle.value)
    error.value = undefined
    isSaving.value = true
    const errorMessage = validateTemplateTitle({
      id: template.id,
      title: templateTitle,
      body: template.body,
      topics: template.topics
    })
    if (errorMessage) {
      error.value = errorMessage
      isSaving.value = false
      putFocusNextTick('rename-template-input')
    } else {
      alertScreenReader('Renaming template')
      renameNoteTemplate(template.id, templateTitle).then(() => {
        isSaving.value = false
        resetTemplate(template, templateTitle)
        alertScreenReader(`Template renamed "${template.title}".`)
        putFocusNextTick('my-templates-button')
        enableFocusLock()
      })
    }
  }
}

const resetTemplate = (template, title) => {
  template.title = title
  updatedTemplateTitle.value = undefined
  templateToDelete.value = undefined
  templateToRename.value = undefined
}
</script>

<style scoped>
.load-note-template-btn {
  height: 24px;
  letter-spacing: normal;
}
.template-actions {
  min-width: 235px !important;
}
</style>
