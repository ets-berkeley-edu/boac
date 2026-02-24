<template>
  <div class="text-center">
    <v-dialog
      v-model="model"
      aria-labelledby="peer-advising-template-modal-header"
      attach="body"
      class="overflow-y-hidden"
      :fullscreen="$vuetify.display.xs"
      max-width="1100"
      min-width="400"
      persistent
      width="90vw"
    >
      <v-card class="modal-content overflow-y-hidden">
        <FocusLock @keydown.esc="cancel">
          <v-card-title>
            <ModalHeader header-id="peer-advising-template-modal-header" :text="title" />
          </v-card-title>
          <v-card-text class="peer-advising-template-modal-content">
            <div class="py-3">
              <v-text-field
                id="peer-advising-note-template-name"
                v-model="templateName"
                aria-describedby="peer-advising-note-template-name-details"
                :aria-invalid="!isValidName"
                aria-required
                autocomplete="on"
                :disabled="isSaving"
                label="Note Template Name"
                :maxlength="maxlength"
                persistent-counter
                required
                :rules="[validateNoteTemplateName]"
                validate-on="lazy invalid-input"
                variant="outlined"
              >
                <template #counter="{max, value}">
                  <CharacterCount :count="toInt(value)" id-prefix="peer-advising-note-template-name" :max="toInt(max)" />
                </template>
                <template #message="{message}">
                  <v-alert
                    id="peer-advising-note-template-name-error"
                    class="font-size-14 line-height-normal"
                    density="compact"
                    role="none"
                    :text="message"
                    type="error"
                    variant="tonal"
                  />
                </template>
              </v-text-field>
            </div>
            <div
              v-if="action !== 'copy'"
              id="note-template-details"
              class="bg-transparent py-3"
            >
              <RichTextEditor
                id="peer-advising-note-template-details-text"
                :disabled="isSaving"
                :initial-value="noteDetailsText ? noteDetailsText : ''"
                label="Note Details"
                :on-value-update="onEditorUpdate"
                :show-advising-note-best-practices="true"
              />
            </div>
            <div v-if="action !== 'copy'" class="py-3">
              <PeerAdvisingNoteTopics
                :topics="topicsSelected"
                :read-only="action === 'view'"
                @update-topics="handleTopicsUpdate"
              />
            </div>
          </v-card-text>
          <v-card-actions class="modal-footer">
            <ProgressButton
              v-if="action !== 'view'"
              id="save-new-peer-advising-note-template"
              :action="saveNoteTemplate"
              :disabled="isValidName !== true || isSaveDisabled"
              :in-progress="isSaving"
              :text="saveButtonText"
            />
            <v-btn
              id="cancel-peer-advising-note-template"
              class="ml-2"
              color="primary"
              text="Cancel"
              variant="text"
              @click="cancel"
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
import {cloneDeep, isEmpty, size, trim} from 'lodash'
import CharacterCount from '@/components/util/CharacterCount.vue'
import ModalHeader from '@/components/util/ModalHeader'
import PeerAdvisingNoteTopics from '@/components/peer/PeerAdvisingNoteTopics.vue'
import ProgressButton from '@/components/util/ProgressButton.vue'
import RichTextEditor from '@/components/util/RichTextEditor.vue'
import {alertScreenReader, putFocusNextTick, toInt} from '@/lib/utils.js'
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
  },
  idToFocusAfterClosing: {
    required: true,
    type: String
  }
})

const isSaving = ref(false)
const isValidName = ref(false)
const model = defineModel({type: Boolean})
const noteDetailsText = ref('')
const templateName = ref('')
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

const isSaveDisabled = computed(() => {
  return !((noteDetailsText.value.length > 0 || topicsSelected.value.length > 0) && templateName.value.length > 0) || props.action === 'view'
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
  putFocusNextTick(props.idToFocusAfterClosing)
}

const handleTopicsUpdate = (newTopics) => {
  topicsSelected.value = newTopics
}

const saveNoteTemplate = () => {
  isSaving.value = true
  if (true === validateNoteTemplateName()) {
    if (props.action === 'edit' && props.selectedNoteTemplate) {
      // Update API call
      updatePeerAdvisingNoteTemplate(props.selectedNoteTemplate.id, noteDetailsText.value, templateName.value, topicsSelected.value).then((updatedNoteTemplate) => {
        model.value = false
        isSaving.value = false
        putFocusNextTick(props.idToFocusAfterClosing)
        emit('note-template-updated', updatedNoteTemplate)
        alertScreenReader(`Updated ${updatedNoteTemplate.title} note template.`)

      })
    } else if (props.action === 'create' || props.action === 'copy') { // This is a new template
      createPeerAdvisingNoteTemplate(props.peerAdvisingDeptId, noteDetailsText.value, templateName.value, topicsSelected.value).then((newNoteTemplate) => {
        model.value = false
        isSaving.value = false
        putFocusNextTick(props.idToFocusAfterClosing)
        emit('note-template-updated', newNoteTemplate)
        alertScreenReader(`Created ${newNoteTemplate.title} note template.`)
      })
    }
  } else {
    putFocusNextTick('peer-advising-note-template-name')
  }
}

const validateNoteTemplateName = () => {
  const name = trim(templateName.value)
  isValidName.value = false
  if (isEmpty(name)) {
    return 'Note template name is required'
  }
  if (size(name) > 255) {
    return 'Note template name must be 255 characters or fewer'
  }
  const msg = isExistingName(name)
  if (size(msg)) {
    return msg
  }
  isValidName.value = true
  return true
}

const isExistingName = (name) => {
  return props.noteTemplates.some(template => (['copy', 'create'].includes(props.action) && template.title === name)
    || (props.action === 'edit' && template.title === name && template.id !== props.selectedNoteTemplate?.id)
  )
    ? `You have an existing template named '${name}'. Please choose a different name.` : false
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
  max-height: fit-content;
  overflow-y: auto;
}
</style>
