<template>
  <div>
    <div v-if="!get(note, 'peerAdvisingDepartment')">
      Loading...
    </div>
    <div v-if="get(note, 'peerAdvisingDepartment')" :class="{'img-blur': currentUser.inDemoMode}">
      <div v-if="note.subject" :id="`note-${note.id}-subject`">{{ note.subject }}</div>
      <div :id="`note-${note.id}-body`" class="note-body" v-html="note.body" />
      <div :id="`note-${note.id}-is-open`" class="w-100" :class="{'demo-mode-blur': currentUser.inDemoMode}">
        <div v-if="note.subject && note.body" class="open-note-message-container pt-2">
          <span :id="`note-${note.id}-message-open`" v-html="note.body" />
        </div>
        <div v-if="note.topics && size(note.topics)" class="mt-4">
          <AdvisingNoteTopics :note="note" read-only />
        </div>
        <div v-if="note.contactType" class="mt-4">
          <div class="font-size-16 font-weight-bold">Contact Type</div>
          <div :id="`note-${note.id}-contact-type`">{{ note.contactType }}</div>
        </div>
      </div>
      <AdvisingNoteAttachments
        v-if="size(note.attachments)"
        :attachments="note.attachments"
        class="attachments-edit mt-4"
        :disabled="false"
        :id-prefix="`note-${note.id}`"
        :is-downloadable="true"
        :is-read-only="true"
        :note="note"
        :note-description="noteDescription"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {get, size} from 'lodash'
import type {Note} from '@/lib/types'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments.vue'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics.vue'
import {useContextStore} from '@/stores/context'

defineProps({
  note: {
    required: false,
    type: Object as PropType<Note>,
    default: undefined
  },
  noteId: {
    required: false,
    type: Number,
    default: undefined
  },
  noteDescription: {
    required: true,
    type: String
  }
})

const currentUser = useContextStore().currentUser
</script>

<style scoped>
:deep(.note-body ul), :deep(.note-body ol) {
  margin: 0 30px 0 30px;
}
.open-note-message-container {
  overflow-wrap: break-word;
}
</style>
