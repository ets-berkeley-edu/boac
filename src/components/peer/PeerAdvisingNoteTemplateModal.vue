<template>
  <div class="pa-4 text-center">
    <v-dialog
      v-model="model"
      max-width="600"
    >
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
              :on-value-update="onEditorUpdate"
              :show-advising-note-best-practices="true"
            />
          </div>
        </div>

        <div class="pr-6 pl-6 pb-3">
          <PeerAdvisingNoteTopics :topics="topicsSelected" @update-topics="handleTopicsUpdate" />
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
          <ProgressButton
            id="save-new-peer-advising-note-template"
            class="float-end"
            :action="saveNoteTemplate"
            :disabled="isSaveDisabled"
            :in-progress="isSaving"
            :text="saveButtonText"
          />
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>

import {computed, onMounted, ref, watch} from 'vue'
import RichTextEditor from '@/components/util/RichTextEditor.vue'
import PeerAdvisingNoteTopics from '@/components/peer/PeerAdvisingNoteTopics.vue'
import {createPeerAdvisingNoteTemplate, updatePeerAdvisingNoteTemplate} from '@/api/peer-advising.js'
import ProgressButton from '@/components/util/ProgressButton.vue'
import {alertScreenReader} from '@/lib/utils.js'

const emit = defineEmits(['note-template-updated'])
const props = defineProps({
  peerAdvisingDeptId: {
    required: true,
    type: Number
  },
  editingNoteTemplate: {
    required: false,
    default: undefined,
    type: Object
  },
  action: {
    required: true,
    type: String
  }
})

const model = defineModel({type: Boolean})
const noteDetailsText = ref('')
const templateName = ref('')
const isSaving = ref(false)
const topicsSelected = ref([])

const isSaveDisabled = computed(() => {
  return !(noteDetailsText.value.length > 0 && templateName.value.length > 0)
})

const saveButtonText = computed(() => {
  if (!props.editingNoteTemplate) {
    return isSaving.value ? 'Saving...' : 'Save Note Template'
  }
  if (isSaving.value) {
    return props.action === 'edit' ? 'Updating...' : 'Copying...'
  }
  return props.action === 'edit' ? 'Update Note Template' : 'Copy Note Template'
})

watch(model, isOpen => {
  if (isOpen) {
    assignEditedNoteTemplateValues()
  }
})

onMounted(() => {
  assignEditedNoteTemplateValues()
})

const assignEditedNoteTemplateValues = () => {
  if (props.editingNoteTemplate && props.action === 'edit' || props.action === 'copy') {
    noteDetailsText.value = props.editingNoteTemplate.body
    templateName.value = props.action === 'copy' ? props.editingNoteTemplate.title + 'Copy' : props.editingNoteTemplate.title
    topicsSelected.value = props.editingNoteTemplate.topics
  } else {
    noteDetailsText.value = ''
    templateName.value = ''
    topicsSelected.value = []
  }
}

const onEditorUpdate = value => {
  noteDetailsText.value = value
}
const cancel = () => {
  model.value = false
}

const handleTopicsUpdate = (newTopics) => {
  topicsSelected.value = newTopics
}

const saveNoteTemplate = () => {
  isSaving.value = true
  if (props.action === 'edit' && props.editingNoteTemplate) {
    // Update API call
    updatePeerAdvisingNoteTemplate(props.editingNoteTemplate.id, noteDetailsText.value, templateName.value, topicsSelected.value).then((updatedNoteTemplate) => {
      model.value = false
      isSaving.value = false
      emit('note-template-updated', updatedNoteTemplate)
      alertScreenReader(`Updated ${updatedNoteTemplate.title} note template.`)
    })
  } else { // This is a new template
    createPeerAdvisingNoteTemplate(props.peerAdvisingDeptId, noteDetailsText.value, templateName.value, topicsSelected.value).then((newNoteTemplate) => {
      model.value = false
      isSaving.value = false
      emit('note-template-updated', newNoteTemplate)
      alertScreenReader(`Created ${newNoteTemplate.title} note template.`)
    })
  }

}
</script>

<style>
#note-template-details .ck-editor__editable {
  height: 180px;
  width: 100%;
}
</style>
