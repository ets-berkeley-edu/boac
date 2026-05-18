<template>
  <div :id="`note-${note.id}-outer`" class="advising-note-outer w-100">
    <div
      :id="`${note.eForm ? 'eForm' : 'note'}-${note.id}-is-closed`"
      :aria-controls="isOpen ? undefined : `note-${note.id}-is-open`"
      :aria-expanded="isOpen ? undefined : false"
      class="d-flex w-100"
      :class="{
        'font-size-18': !note.peerAdvisingDepartmentId,
        'cursor-pointer note-snippet-when-closed': !isOpen
      }"
      :role="isOpen ? undefined : 'button'"
      :tabindex="isOpen ? undefined : 0"
      @click="onClickOpen"
      @keyup.enter="onClickOpen"
    >
      <div v-if="note.isDraft" :id="`note-${note.id}-is-draft`" class="d-flex align-center">
        <v-badge
          :aria-atomic="undefined"
          :aria-label="undefined"
          :aria-live="undefined"
          class="mr-1"
          color="error"
          inline
          role="none"
        >
          <template #badge>
            <span class="font-weight-black pa-1 text-body-2 line-height-1">Draft</span>
          </template>
        </v-badge>
        <span :id="`note-${note.id}-subject`" class="text-no-wrap">{{ note.subject || contextStore.config.draftNoteSubjectPlaceholder }}</span>
      </div>
      <div
        v-if="!note.isDraft"
        :id="`note-${note.id}-subject`"
        :class="{'truncate-with-ellipsis': !isOpen}"
        v-html="noteSummary"
      />
      <TimelineMessageIcons v-if="!isOpen" :message="note" />
    </div>
    <section
      :id="`note-${note.id}-is-open`"
      class="note-body"
      :class="{'sr-only': !isOpen}"
    >
      <div v-if="(note.subject || note.isDraft) && note.message" class="open-note-message-container py-3">
        <span :id="`note-${note.id}-message-open`" v-html="note.message" />
      </div>
      <div v-if="!note.subject && !note.message && note.eForm" class="py-3">
        <AdvisingEForm :note="note" />
      </div>
      <div v-if="!note.eForm && note.legacySource" class="font-italic text-medium-emphasis">
        (note imported from {{ note.legacySource }})
      </div>
      <AdvisingNoteTopics
        v-if="note.topics && size(note.topics)"
        class="mt-5"
        label-class="text-medium-emphasis"
        :note="note"
        read-only
      />
      <div v-if="note.contactType" class="mt-5">
        <div class="font-size-16 font-weight-bold text-medium-emphasis">Contact Type</div>
        <div :id="`note-${note.id}-contact-type`">{{ note.contactType }}</div>
      </div>
      <div v-if="showNoteAttachmentsWidget" class="note-attachments-container mt-1">
        <AdvisingNoteAttachments
          :add="addNoteAttachments"
          :attachments="note.attachments || []"
          class="attachments-edit py-3"
          :disabled="!!(isUpdatingAttachments || noteStore.boaSessionExpired)"
          :id-prefix="`note-${note.id}`"
          :is-downloadable="true"
          :is-read-only="!!note.legacySource || !canUserEditNote(note, currentUser)"
          label-class="text-medium-emphasis"
          :note="note"
          :remove="removeAttachmentByIndex"
        />
      </div>
    </section>
    <AreYouSureModal
      v-model="showConfirmDeleteAttachment"
      button-label-confirm="Delete"
      :function-cancel="cancelRemoveAttachment"
      :function-confirm="confirmedRemoveAttachment"
      modal-header="Delete Attachment"
    >
      Are you sure you want to delete the <strong>'{{ attachmentToDelete.displayName }}'</strong> attachment?
    </AreYouSureModal>
  </div>
</template>

<script setup>
import {computed, ref} from 'vue'
import {size} from 'lodash'
import AdvisingEForm from '@/components/note/eform/AdvisingEForm'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import TimelineMessageIcons from '@/components/student/profile/academic-timeline/TimelineMessageIcons.vue'
import {addAttachments, removeAttachment} from '@/api/notes'
import {alertScreenReader} from '@/lib/utils'
import {canUserEditNote, summarizeNoteForAcademicTimeline} from '@/lib/note.js'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  afterSaved: {
    required: true,
    type: Function
  },
  editNote: {
    required: true,
    type: Function
  },
  isOpen: {
    required: true,
    type: Boolean
  },
  note: {
    required: true,
    type: Object
  },
  onClickOpen: {
    required: true,
    type: Function
  }
})

const contextStore = useContextStore()
const noteStore = useNoteStore()

const addAttachmentInputElementId = `note-${props.note.id}-choose-file-for-note-attachment`
const attachmentToDelete = ref()
const currentUser = contextStore.currentUser
const isUpdatingAttachments = ref(false)
const noteSummary = computed(() => {
  const note = props.note
  const showNoteMessage = props.isOpen && !note.subject && !note.peerAdvisingDepartmentId && size(note.message)
  return showNoteMessage ? note.message : summarizeNoteForAcademicTimeline(note, !props.isOpen)
})
const showConfirmDeleteAttachment = ref(false)
const showNoteAttachmentsWidget = computed(() => (!props.note.legacySource && canUserEditNote(props.note, currentUser)) || size(props.note.attachments))

const addNoteAttachments = attachments => {
  return new Promise(resolve => {
    isUpdatingAttachments.value = true
    noteStore.setModel(props.note)
    addAttachments(props.note.id, attachments).then(updatedNote => {
      props.afterSaved(updatedNote, addAttachmentInputElementId)
      noteStore.setAttachments(updatedNote.attachments)
      isUpdatingAttachments.value = false
      resolve()
    })
  })
}

const cancelRemoveAttachment = () => {
  showConfirmDeleteAttachment.value = false
  attachmentToDelete.value = null
}

const confirmedRemoveAttachment = () => {
  showConfirmDeleteAttachment.value = false
  const attachment = attachmentToDelete.value
  if (attachment && attachment.id) {
    removeAttachment(props.note, attachment.id).then(updatedNote => {
      alertScreenReader(`Removed attachment "${attachment.displayName}"`)
      props.afterSaved(updatedNote, addAttachmentInputElementId)
    })
  }
}

const removeAttachmentByIndex = index => {
  attachmentToDelete.value = props.note.attachments[index]
  showConfirmDeleteAttachment.value = true
}
</script>

<style>
.open-note-message-container ul {
  margin: 0 30px 0 30px;
}
</style>

<style scoped>
.advising-note-outer {
  box-sizing: border-box;
}
.attachments-edit {
  box-sizing: border-box;
  max-width: 100%;
  width: 100%;
}
.open-note-message-container {
  overflow-wrap: break-word;
}
.note-snippet-when-closed {
  font-size: 1rem !important;
  height: 24px;
}
</style>
