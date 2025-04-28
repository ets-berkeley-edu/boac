<template>
  <div class="d-flex justify-space-between">
    <div>
      <ModalHeader header-id="peer-advising-note-modal-header" :text="headerText" />
    </div>
    <div class="px-4">
      <SelectPeerAdvisingNoteTemplateForNote
        v-if="isMounted"
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
import {onMounted, ref} from 'vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import type {NoteTemplate} from '@/lib/types'
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
    type: Array<NoteTemplate>
  },
  isNoteTemplatesLoading: {
    required: true,
    type: Boolean
  }
})

const isMounted = ref(false)

onMounted(() => {
  // EditPeerAdvisingNoteHeader must be mounted before SelectPeerAdvisingNoteTemplateForNote
  // attaches its menu to the ModalHeader.
  isMounted.value = true
})

const templateSelected = (template: NoteTemplate) => {
  emit('template-selected', template)
  alertScreenReader(`Using template ${template.title}.`)
  putFocusNextTick('find-student-autocomplete-input')
}
</script>
