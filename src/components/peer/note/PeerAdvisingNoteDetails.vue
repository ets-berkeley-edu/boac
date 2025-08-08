<template>
  <div>
    <div :class="{'img-blur': currentUser.inDemoMode}">
      <div v-if="note.subject" :id="`note-${note.id}-subject`">{{ note.subject }}</div>
      <div :id="`note-${note.id}-body`" class="note-body" v-html="note.body" />
      <div :id="`note-${note.id}-is-open`" class="w-100" :class="{'demo-mode-blur': currentUser.inDemoMode}">
        <div v-if="note.subject && note.body" class="open-note-message-container pt-2">
          <span :id="`note-${note.id}-message-open`" v-html="note.body" />
        </div>
        <div v-if="note.topics && size(note.topics)" class="mt-5">
          <AdvisingNoteTopics :note="note" read-only />
        </div>
        <div v-if="note.contactType" class="mt-5">
          <div class="font-size-16 font-weight-bold text-medium-emphasis">Contact Type</div>
          <div :id="`note-${note.id}-contact-type`">{{ note.contactType }}</div>
        </div>
      </div>
      <AdvisingNoteAttachments
        v-if="canUserEditNote(note, currentUser) || note.attachments.length"
        :add="addNoteAttachments"
        :attachments="note.attachments"
        class="attachments-edit mt-5"
        :disabled="false"
        :id-prefix="`note-${note.id}`"
        :is-downloadable="true"
        :is-read-only="!canUserEditNote(note, currentUser)"
        :note="note"
        :note-description="noteDescription"
        :remove="removeAttachmentByIndex"
      />
      <AreYouSureModal
        v-model="showConfirmDeleteAttachment"
        button-label-confirm="Delete"
        :function-cancel="cancelRemoveAttachment"
        :function-confirm="confirmedRemoveAttachment"
        modal-header="Delete Attachment"
      >
        Are you sure you want to delete the <strong>'{{ note.attachments[deleteAttachmentIndex].displayName }}'</strong> attachment?
      </AreYouSureModal>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {ref} from 'vue'
import {size} from 'lodash'
import type {Note, NoteAttachment} from '@/lib/types'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments.vue'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics.vue'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import {addPeerAdvisingAttachments} from '@/api/peer-advising-notes'
import {alertScreenReader} from '@/lib/utils'
import {canUserEditNote} from '@/lib/note'
import {removeAttachment} from '@/api/notes'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  afterNoteEdit: {
    required: true,
    type: Function
  },
  note: {
    required: true,
    type: Object as PropType<Note>
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

const addAttachmentInputElementId = `note-${props.note.id}-choose-file-for-note-attachment`
const currentUser = useContextStore().currentUser
const deleteAttachmentIndex = ref<number>(NaN)
const isUpdatingAttachments = ref<boolean>()
const showConfirmDeleteAttachment = ref(false)

const addNoteAttachments = (attachments: NoteAttachment[]) => {
  return new Promise<void>(resolve => {
    isUpdatingAttachments.value = true
    addPeerAdvisingAttachments(props.note.id, attachments).then(() => {
      props.afterNoteEdit(props.note.id, addAttachmentInputElementId)
      alertScreenReader('Attachment added', false, 'assertive')
      isUpdatingAttachments.value = false
      resolve()
    })
  })
}

const cancelRemoveAttachment = () => {
  showConfirmDeleteAttachment.value = false
  deleteAttachmentIndex.value = NaN
}

const confirmedRemoveAttachment = () => {
  showConfirmDeleteAttachment.value = false
  const attachment = props.note.attachments[deleteAttachmentIndex.value]
  if (attachment && attachment.id) {
    removeAttachment(props.note, attachment.id).then(() => {
      alertScreenReader(`Attachment "${attachment.displayName}" removed`)
      props.afterNoteEdit(props.note.id, addAttachmentInputElementId)
    })
  }
}

const removeAttachmentByIndex = (index: number) => {
  deleteAttachmentIndex.value = index
  showConfirmDeleteAttachment.value = true
}
</script>

<style scoped>
:deep(.note-body ul), :deep(.note-body ol) {
  margin: 0 30px 0 30px;
}
.open-note-message-container {
  overflow-wrap: break-word;
}
</style>
