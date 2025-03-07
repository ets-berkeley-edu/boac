<template>
  <div class="d-flex justify-space-between">
    <div>
      <ModalHeader :text="headerText" />
    </div>
    <div>
      <SelectPeerAdvisingNoteTemplateForNote
        :note-templates="noteTemplates"
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
  }
})

const templateSelected = (template) => {
  emit('template-selected', template)
}
</script>
