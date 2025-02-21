<template>
  <div class="pa-4 text-center">
    <v-dialog
      v-model="dialog"
      max-width="600"
    >
      <template #activator="{ props: activatorProps }">
        <v-btn
          id="create-new-peer-advising-note-template"
          class="float-end"
          color="primary"
          slim
          text="Create new Note Template"
          variant="text"
          :prepend-icon="mdiPlus"
          v-bind="activatorProps"
        />
      </template>

      <v-card>
        <template #title>
          <span class="text-h5">Create New Note Template</span>
        </template>
        <v-divider class="border-opacity-50"></v-divider>

        <div class="pt-6 pl-6 pr-6">
          <div>
            <v-text-field
              id="peer-advising-note-template-name-text"
              v-model="templateName"
              label="Note Template Name"
              variant="outlined"
            >
            </v-text-field>
          </div>
        </div>
        <div class="pb-6 pl-6 pr-6">
          <div id="note-template-details" class="bg-transparent mt-2">
            <RichTextEditor
              id="peer-advising-note-template-details-text"
              :disabled="isSaving"
              :initial-value="noteDetailsText ? noteDetailsText : ''"
              label="Note Details"
              :showAdvisingNoteBestPractices="true"
              :on-value-update="onEditorUpdate"
            />
          </div>
        </div>

        <div class="pr-6 pl-6 pb-3">
          <PeerAdvisingNoteTopics @update-topics="handleTopicsUpdate" />
        </div>

        <v-divider class="border-opacity-50"></v-divider>

        <div class="footer pt-4 pr-6 pb-6">
          <v-btn
            id="cancel-peer-advising-note-template"
            class="float-end ml-3"
            color="primary"
            text="Cancel"
            variant="text"
            @click="cancel"
          />
          <v-btn
            id="save-new-peer-advising-note-template"
            class="float-end"
            color="primary"
            text="Save Template"
            @click="saveNoteTemplate"
          />
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>

import {mdiPlus} from '@mdi/js'
import {ref} from 'vue'
import RichTextEditor from '@/components/util/RichTextEditor.vue'
import PeerAdvisingNoteTopics from '@/components/peer/PeerAdvisingNoteTopics.vue'
import {createPeerAdvisingNoteTemplate} from '@/api/peer-advising.js'

const props = defineProps({
  peerAdvisingDeptId: {
    required: true,
    type: Number
  }
})

const dialog = ref()
const noteDetailsText = ref('')
const templateName = ref('')
const isSaving = ref(false)
const topicsSelected = ref([])

const onEditorUpdate = value => {
  noteDetailsText.value = value
}
const cancel = () => {
  dialog.value = false
}

const handleTopicsUpdate = (newTopics) => {
  topicsSelected.value = newTopics
}

const saveNoteTemplate = () => {
  createPeerAdvisingNoteTemplate(props.peerAdvisingDeptId, noteDetailsText.value, templateName.value, topicsSelected.value).then(() => {
    dialog.value = false
  })
}
</script>

<style scoped>
hr {
  margin-top: 0px !important;
  margin-bottom: 0px !important;
}
</style>