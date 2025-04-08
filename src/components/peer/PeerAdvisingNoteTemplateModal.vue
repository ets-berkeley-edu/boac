<template>
  <div class="text-center">
    <v-dialog
      v-model="model"
      aria-labelledby="peer-advising-template-modal-header"
      attach="body"
      persistent
    >
      <v-card class="modal-content overflow-y-hidden" width="600">
        <FocusLock @keydown.esc="cancel">
          <v-card-title>
            <ModalHeader header-id="peer-advising-template-modal-header" :text="title" />
          </v-card-title>
          <v-card-text class="peer-advising-template-modal-content">
            <div class="py-3">
              <v-text-field
                id="peer-advising-note-template-name-text"
                v-model="templateName"
                counter="255"
                :disabled="isSaving"
                label="Note Template Name"
                variant="outlined"
                :maxlength="maxlength"
                persistent-counter
                required
                :rules="[() => isValidName]"
                validate-on="lazy input"
              >
                <template #counter>
                  <div>
                    {{ size(templateName) ? `${maxlength} character limit (${maxlength - size(templateName)} left)` : `${maxlength} character limit` }}
                  </div>
                </template>
              </v-text-field>
            </div>
            <div
              v-if="action !== 'copy'"
              id="note-template-details"
              class="bg-transparent pb-3"
            >
              <RichTextEditor
                id="peer-advising-note-template-details-text"
                :disabled="isSaving"
                :initial-value="noteDetailsText ? noteDetailsText : ''"
                label="Note Details"
                :on-value-update="onEditorUpdate"
                :is-in-modal="true"
                :show-advising-note-best-practices="true"
              />
            </div>
            <div v-if="action !== 'copy'" class="pb-3">
              <PeerAdvisingNoteTopics
                :topics="topicsSelected"
                :read-only="action === 'view'"
                @update-topics="handleTopicsUpdate"
              />
            </div>
          </v-card-text>
          <v-card-actions class="justify-end">
            <v-btn
              id="cancel-peer-advising-note-template"
              class="float-end ml-3"
              color="primary"
              text="Cancel"
              variant="text"
              @click="cancel"
            />
            <ProgressButton
              v-if="action !== 'view'"
              id="save-new-peer-advising-note-template"
              class="float-end"
              :action="saveNoteTemplate"
              :disabled="isValidName !== true || isSaveDisabled"
              :in-progress="isSaving"
              :text="saveButtonText"
            />
          </v-card-actions>
        </FocusLock>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import FocusLock from 'vue-focus-lock'
import {computed, onMounted, ref, watch} from 'vue'
import {cloneDeep, isEmpty, size} from 'lodash'
import ModalHeader from '@/components/util/ModalHeader'
import PeerAdvisingNoteTopics from '@/components/peer/PeerAdvisingNoteTopics.vue'
import ProgressButton from '@/components/util/ProgressButton.vue'
import RichTextEditor from '@/components/util/RichTextEditor.vue'
import {alertScreenReader} from '@/lib/utils.js'
import {createPeerAdvisingNoteTemplate, updatePeerAdvisingNoteTemplate} from '@/api/peer-advising-notes.js'

const emit = defineEmits(['note-template-updated'])
const props = defineProps({
  peerAdvisingDeptId: {
    required: true,
    type: Number
  },
  selectedNoteTemplate: {
    required: false,
    default: undefined,
    type: Object
  },
  action: {
    required: true,
    type: String
  },
  noteTemplates: {
    required: true,
    type: Array
  }
})

const model = defineModel({type: Boolean})
const noteDetailsText = ref('')
const templateName = ref('')
const isSaving = ref(false)
const topicsSelected = ref([])
const maxlength = 255

const title = computed(() => {
  switch (props.action) {
  case 'view':
    return 'View Note Template'
  case 'edit':
    return 'Edit Note Template'
  case 'copy':
    return 'Copy Note Template'
  case 'create':
    return 'Create Note Template'
  default: // Should never happen!!
    return 'Create Note Template'
  }
})

const isValidName = computed(() => validateNoteTemplateName(templateName.value))

const isSaveDisabled = computed(() => {
  return !(noteDetailsText.value.length > 0 && templateName.value.length > 0) || props.action === 'view'
})

const saveButtonText = computed(() => {
  if (!props.selectedNoteTemplate) {
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
  if (props.selectedNoteTemplate && ['copy', 'edit', 'view'].includes(props.action)) {
    noteDetailsText.value = props.selectedNoteTemplate.body
    templateName.value = props.action === 'copy' ? props.selectedNoteTemplate.title + ' Copy' : props.selectedNoteTemplate.title
    topicsSelected.value = cloneDeep(props.selectedNoteTemplate.topics)
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
  if (props.action === 'edit' && props.selectedNoteTemplate) {
    // Update API call
    updatePeerAdvisingNoteTemplate(props.selectedNoteTemplate.id, noteDetailsText.value, templateName.value, topicsSelected.value).then((updatedNoteTemplate) => {
      model.value = false
      isSaving.value = false
      emit('note-template-updated', updatedNoteTemplate)
      alertScreenReader(`Updated ${updatedNoteTemplate.title} note template.`)
    })
  } else if (props.action === 'create' || props.action === 'copy') { // This is a new template
    createPeerAdvisingNoteTemplate(props.peerAdvisingDeptId, noteDetailsText.value, templateName.value, topicsSelected.value).then((newNoteTemplate) => {
      model.value = false
      isSaving.value = false
      emit('note-template-updated', newNoteTemplate)
      alertScreenReader(`Created ${newNoteTemplate.title} note template.`)
    })
  }
}

const validateNoteTemplateName = (name) => {
  if (isEmpty(name)) {
    return 'Name is required'
  }
  if (size(name) > 255) {
    return 'Name must be 255 characters or fewer'
  }
  const msg = isExistingName(name)
  return msg && size(msg) ? msg : true
}

const isExistingName = (name) => {
  return props.noteTemplates.some(template => (['copy', 'create'].includes(props.action) && template.title === name)
    || (props.action === 'edit' && template.title === name && template.id !== props.selectedNoteTemplate?.id)
  )
    ? 'Name already exists. Please choose a different name.' : false
}



</script>

<style>
.ck-balloon-panel {
  z-index: 9999 !important;
}
#note-template-details .ck-editor__editable {
  height: 180px;
  width: 100%;
}
.peer-advising-template-modal-content {
  height: calc(100vh - 215px);
  overflow-y: auto;
}
</style>
