<template>
  <div class="d-flex justify-space-between">
    <div>
      <ModalHeader header-id="peer-advising-note-modal-header" :text="headerText" />
    </div>
    <div>
      <SelectPeerAdvisingNoteTemplateForNote
        :note-templates="noteTemplates"
        :is-note-templates-loading="isNoteTemplatesLoading"
        :exit="noop"
        @template-selected="templateSelected"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import {noop} from 'lodash'
import ModalHeader from '@/components/util/ModalHeader.vue'
import SelectPeerAdvisingNoteTemplateForNote from '@/components/peer/note/SelectPeerAdvisingNoteTemplateForNote.vue'

const emit = defineEmits([
  'template-selected'
])

defineProps({
  headerText: {
    required: true,
    type: String
  },
  noteTemplates: {
    required: true,
    type: Array
  },
  isNoteTemplatesLoading: {
    required: true,
    type: Boolean
  }
})

const templateSelected = (template) => {
  emit('template-selected', template)
}
</script>
