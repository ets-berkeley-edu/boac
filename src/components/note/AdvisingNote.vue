<template>
  <article :id="`note-${note.id}-outer`" class="advising-note-outer w-100">
    <div
      :id="`note-${note.id}-is-closed`"
      aria-level="3"
      class="d-flex w-100"
      :class="{
        'font-size-18': !note.peerAdvisingDepartmentId,
        'note-snippet-when-closed': !isOpen
      }"
      role="heading"
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
            <span class="font-weight-black pa-1 text-body-2">Draft</span>
          </template>
        </v-badge>
        <span :id="`note-${note.id}-subject`">{{ note.subject || contextStore.config.draftNoteSubjectPlaceholder }}</span>
      </div>
      <div
        v-if="!note.isDraft"
        :id="`note-${note.id}-subject`"
        :class="{'truncate-with-ellipsis': !isOpen}"
        v-html="noteSummary"
      />
      <div v-if="!isOpen && size(note.attachments)" class="px-2 ml-auto">
        <v-icon :aria-hidden="true" color="info" :icon="mdiPaperclip" />
        <span class="sr-only">Has attachments</span>
      </div>
    </div>
    <section
      :id="`note-${note.id}-is-open`"
      class="pb-4"
      :class="{'sr-only': !isOpen}"
    >
      <div v-if="(note.subject || note.isDraft) && note.message" class="open-note-message-container py-3">
        <span :id="`note-${note.id}-message-open`" v-html="note.message" />
      </div>
      <div v-if="!note.subject && !note.message && note.eForm" class="py-3">
        <AdvisingEForm :note="note" />
      </div>
      <div v-if="isAuthorDetailsLoaded && !isNil(author) && !author.name && !author.email && !note.eForm" class="font-size-14 py-3 text-medium-emphasis">
        Advisor profile not found
        <span v-if="note.legacySource" class="font-italic">
          (note imported from {{ note.legacySource }})
        </span>
      </div>
      <div v-if="isAuthorDetailsLoaded && author && !note.eForm" class="py-3">
        <div v-if="author.name || author.email">
          <span class="sr-only">Note created by </span>
          <span v-if="author.uid && author.name">
            <router-link
              v-if="currentUser.isAdmin && note.peerAdvisingDepartmentId"
              :id="`note-${note.id}-link-to-peer-advisor-home`"
              :to="`/peer_advisor/${author.uid}/home`"
            >
              {{ author.name }}
            </router-link>
            <a
              v-if="!currentUser.isAdmin || !note.peerAdvisingDepartmentId"
              :id="`note-${note.id}-author-name`"
              :aria-label="`${author.name} UC Berkeley Directory page (opens in new tab)`"
              :href="`https://www.berkeley.edu/directory/results?search-term=${author.name}`"
              target="_blank"
            >
              {{ author.name }}
            </a>
          </span>
          <span v-if="!author.uid && author.name" :id="`note-${note.id}-author-name`">
            {{ author.name }}
          </span>
          <span v-if="!author.uid && !author.name && author.email" :id="`note-${note.id}-author-email`">
            {{ author.email }}
          </span>
          <span v-if="author.role || author.title">
            - <span :id="`note-${note.id}-author-role`">{{ capitalizeAllWords(replace(author.role || author.title, '_', ' ')) }}</span>
          </span>
          <span v-if="note.legacySource" class="font-italic text-medium-emphasis">
            (note imported from {{ note.legacySource }})
          </span>
        </div>
        <div v-if="note.peerAdvisingDepartmentId">
          <span :id="`note-${note.id}-peer-advising-department`">{{ peerAdvisingDepartment.name }}</span>
          <div
            v-if="peerAdvisingDepartment.deptName !== peerAdvisingDepartment.name"
            :id="`note-${note.id}-university-department-of-peer-advisor`"
            class="text-medium-emphasis"
          >
            {{ peerAdvisingDepartment.deptName }}
          </div>
        </div>
        <div v-if="!note.peerAdvisingDepartmentId" class="text-medium-emphasis">
          <div v-for="(deptName, index) in authorDepartments" :key="index">
            <span :id="`note-${note.id}-author-dept-${index}`">{{ deptName }}</span>
          </div>
        </div>
      </div>
      <div v-if="note.topics && size(note.topics)" class="mt-5">
        <AdvisingNoteTopics
          label-class="text-medium-emphasis"
          :note="note"
          read-only
        />
      </div>
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
          label-class="text-medium-emphasis"
          :note="note"
          :read-only="!!note.legacySource || !canUserEditNote(note, currentUser)"
          :remove="removeAttachmentByIndex"
        />
      </div>
    </section>
    <AdvisingNoteComments
      v-if="!note.legacySource && !note.eform && !note.peerAdvisingDepartmentId"
      class="border-t-sm py-4"
      :class="{'sr-only': !isOpen}"
      :note="note"
    />
    <AreYouSureModal
      v-model="showConfirmDeleteAttachment"
      button-label-confirm="Delete"
      :function-cancel="cancelRemoveAttachment"
      :function-confirm="confirmedRemoveAttachment"
      modal-header="Delete Attachment"
    >
      Are you sure you want to delete the <strong>'{{ attachmentToDelete.displayName }}'</strong> attachment?
    </AreYouSureModal>
  </article>
</template>

<script setup>
import {computed, onMounted, ref, watch} from 'vue'
import {get, isNil, map, orderBy, replace, size} from 'lodash'
import {mdiPaperclip} from '@mdi/js'
import AdvisingEForm from '@/components/note/eform/AdvisingEForm'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments'
import AdvisingNoteComments from '@/components/note/comment/AdvisingNoteComments'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import {addAttachments, removeAttachment} from '@/api/notes'
import {alertScreenReader, capitalizeAllWords, oxfordJoin} from '@/lib/utils'
import {canUserEditNote, summarizeNoteForAcademicTimeline} from '@/lib/note.js'
import {findPeerAdvisingDepartment, getBoaUserRoles} from '@/lib/berkeley-department'
import {getCalnetProfileByCsid, getCalnetProfileByUid} from '@/api/user'
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
  }
})

const contextStore = useContextStore()
const noteStore = useNoteStore()

const addAttachmentInputElementId = `note-${props.note.id}-choose-file-for-note-attachment`
const attachmentToDelete = ref()
const author = ref(get(props.note, 'author'))
const authorDepartments = computed(() => orderBy(map(author.value.departments, 'deptName')))
const currentUser = contextStore.currentUser
const isAuthorDetailsLoaded = ref(false)
const isUpdatingAttachments = ref(false)
const noteSummary = computed(() => {
  const note = props.note
  const showNoteMessage = props.isOpen && !note.subject && !note.peerAdvisingDepartmentId && size(note.message)
  return showNoteMessage ? note.message : summarizeNoteForAcademicTimeline(note, !props.isOpen)
})
const peerAdvisingDepartment = computed(() => props.note.peerAdvisingDepartmentId ? findPeerAdvisingDepartment(props.note.peerAdvisingDepartmentId) : undefined)
const showConfirmDeleteAttachment = ref(false)
const showNoteAttachmentsWidget = computed(() => (!props.note.legacySource && canUserEditNote(props.note, currentUser)) || size(props.note.attachments))

watch(() => props.isOpen, () => {
  loadAuthorDetails()
})

onMounted(() => {
  loadAuthorDetails()
})

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

const loadAuthorDetails = () => {
  const requiresLazyLoad = (
    props.isOpen &&
    (
      !get(props.note, 'author.name') ||
      !get(props.note, 'author.role') ||
      get(author.value, 'uid') !== get(props.note, 'author.uid') ||
      get(author.value, 'sid') !== get(props.note, 'author.sid')
    )
  )
  if (requiresLazyLoad) {
    const hasIdentifier = get(props.note, 'author.uid') || get(props.note, 'author.sid')
    if (hasIdentifier) {
      const author_uid = props.note.author.uid
      const callback = data => {
        author.value = data
        author.value.role = author.value.role || author.value.title
        if (!author.value.role && author.value.departments.length) {
          author.value.role = oxfordJoin(getBoaUserRoles(author.value.departments[0]))
        }
      }
      if (author_uid) {
        if (author_uid === currentUser.uid) {
          callback(currentUser)
          isAuthorDetailsLoaded.value = true
        } else {
          getCalnetProfileByUid(author_uid).then(callback).finally(() => isAuthorDetailsLoaded.value = true)
        }
      } else if (props.note.author.sid) {
        getCalnetProfileByCsid(props.note.author.sid).then(callback).finally(() => isAuthorDetailsLoaded.value = true)
      }
    } else {
      isAuthorDetailsLoaded.value = true
    }
  } else {
    isAuthorDetailsLoaded.value = true
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
  font-weight: 400;
  height: 24px;
}
</style>
