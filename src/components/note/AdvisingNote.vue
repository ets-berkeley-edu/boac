<template>
  <div :id="`note-${note.id}-outer`" class="advising-note-outer">
    <div :id="`note-${note.id}-is-closed`" :class="{'note-snippet-when-closed truncate-with-ellipsis': !isOpen}" aria-label="Advising note">
      <span v-if="note.isDraft" :id="`note-${note.id}-is-draft`">
        <span class="pr-2">
          <v-badge rounded color="warning">Draft</v-badge>
        </span>
        <span :id="`note-${note.id}-subject`">{{ note.subject || contextStore.config.draftNoteSubjectPlaceholder }}</span>
      </span>
      <span v-if="!note.isDraft">
        <span v-if="note.subject" :id="`note-${note.id}-subject`">{{ note.subject }}</span>
        <span v-if="!note.subject && size(note.message)" :id="`note-${note.id}-subject`">
          <span v-if="isOpen" v-html="note.message" />
          <span v-if="!isOpen" v-html="stripHtmlAndTrim(note.message).replace(/\n\r/g, ' ')" />
        </span>
        <span v-if="!note.subject && !size(note.message) && note.category" :id="`note-${note.id}-subject`">{{ note.category }}<span v-if="note.subcategory">, {{ note.subcategory }}</span></span>
        <span v-if="!note.subject && !size(note.message) && !note.category && !note.eForm" :id="`note-${note.id}-category-closed`">{{ !isEmpty(note.author.departments) ? note.author.departments[0].name : '' }}
          advisor {{ author.name }}<span v-if="note.topics && size(note.topics)">: {{ oxfordJoin(note.topics) }}</span>
        </span>
        <span v-if="!note.subject && !size(note.message) && !note.category && note.eForm" :id="`note-${note.id}-subject`">
          eForm: {{ note.eForm.action }} &mdash; {{ note.eForm.status }}
        </span>
      </span>
    </div>
    <div v-if="isOpen" :id="`note-${note.id}-is-open`">
      <div v-if="!note.legacySource">
        <v-btn
          v-if="currentUser.isAdmin"
          :id="`btn-delete-note-${note.id}`"
          class="sr-only"
          @click.stop="deleteNote(note)"
        >
          Delete Note
        </v-btn>
        <v-btn
          v-if="currentUser.uid === author.uid"
          :id="`btn-edit-note-${note.id}`"
          class="sr-only"
          @click.stop="editNote(note)"
        >
          Edit Note
        </v-btn>
      </div>
      <div v-if="note.subject && note.message" class="mt-2">
        <span :id="`note-${note.id}-message-open`" v-html="note.message"></span>
      </div>
      <div v-if="!note.subject && !note.message && note.eForm" class="mt-2">
        <dl :id="`note-${note.id}-message-open`">
          <div>
            <dt>Term</dt>
            <dd>{{ termNameForSisId(note.eForm.term) }}</dd>
          </div>
          <div>
            <dt>Course</dt>
            <dd>{{ note.eForm.sectionId }} {{ note.eForm.courseName }} - {{ note.eForm.courseTitle }} {{ note.eForm.section }}</dd>
          </div>
          <div>
            <dt>Action</dt>
            <dd>
              {{ note.eForm.action }}
              <span v-if="note.eForm.action === 'Late Grading Basis Change' && note.eForm.gradingBasis"> from <span class="font-italic">{{ note.eForm.gradingBasis }}</span></span>
              <span v-if="note.eForm.action === 'Late Grading Basis Change' && note.eForm.requestedGradingBasis"> to <span class="font-italic">{{ note.eForm.requestedGradingBasis }}</span></span>
              <span v-if="note.eForm.action === 'Unit Change' && note.eForm.unitsTaken"> from <span class="font-italic">{{ numFormat(note.eForm.unitsTaken, '0.0') }}</span>{{ 1 === toInt(note.eForm.unitsTaken) ? ' unit' : ' units' }}</span>
              <span v-if="note.eForm.action === 'Unit Change' && note.eForm.requestedUnitsTaken"> to <span class="font-italic">{{ numFormat(note.eForm.requestedUnitsTaken, '0.0') }}</span>{{ 1 === toInt(note.eForm.requestedUnitsTaken) ? ' unit' : ' units' }}</span>
            </dd>
          </div>
          <div>
            <dt>Form ID</dt>
            <dd>{{ note.eForm.id }}</dd>
          </div>
          <div>
            <dt>Date Initiated</dt>
            <dd>{{ DateTime.fromJSDate(note.createdAt).toFormat('MM/dd/yyyy') }}</dd>
          </div>
          <div>
            <dt>Form Status </dt>
            <dd>{{ note.eForm.status }}</dd>
          </div>
          <div>
            <dt>Final Date &amp; Time Stamp</dt>
            <dd>{{ DateTime.fromJSDate(note.updatedAt).toFormat('MM/dd/yyyy h:mm:ssa') }}</dd>
          </div>
        </dl>
      </div>
      <div v-if="!isNil(author) && !author.name && !author.email && !note.eForm" class="font-size-14 mt-2 text-black-50">
        Advisor profile not found
        <span v-if="note.legacySource" class="font-italic">
          (note imported from {{ note.legacySource }})
        </span>
      </div>
      <div v-if="author" class="mt-2">
        <div v-if="author.name || author.email">
          <span class="sr-only">Note created by </span>
          <a
            v-if="author.uid && author.name"
            :id="`note-${note.id}-author-name`"
            :aria-label="`Open UC Berkeley Directory page of ${author.name} in a new window`"
            :href="`https://www.berkeley.edu/directory/results?search-term=${author.name}`"
            target="_blank"
          >{{ author.name }}</a>
          <span v-if="!author.uid && author.name" :id="`note-${note.id}-author-name`">
            {{ author.name }}
          </span>
          <span v-if="!author.uid && !author.name && author.email" :id="`note-${note.id}-author-email`">
            {{ author.email }}
          </span>
          <span v-if="author.role || author.title">
            - <span :id="`note-${note.id}-author-role`" class="text-dark">{{ author.role || author.title }}</span>
          </span>
          <span v-if="note.legacySource" class="font-italic text-black-50">
            (note imported from {{ note.legacySource }})
          </span>
        </div>
        <div v-if="size(author.departments)" class="text-medium-emphasis">
          <div v-for="(deptName, index) in authorDepartments" :key="index">
            <span :id="`note-${note.id}-author-dept-${index}`">{{ deptName }}</span>
          </div>
        </div>
      </div>
      <div v-if="note.topics && size(note.topics)">
        <div class="pill-list-header mt-3">{{ size(note.topics) === 1 ? 'Topic Category' : 'Topic Categories' }}</div>
        <ul class="pill-list pl-0">
          <li
            v-for="(topic, index) in note.topics"
            :id="`note-${note.id}-topic-${index}`"
            :key="topic"
          >
            <span class="pill pill-attachment text-uppercase text-no-wrap">{{ topic }}</span>
          </li>
        </ul>
      </div>
      <div v-if="note.contactType" class="mt-3">
        <div class="font-weight-bold">Contact Type</div>
        <div :id="`note-${note.id}-contact-type`">{{ note.contactType }}</div>
      </div>
    </div>
    <AreYouSureModal
      v-model="showConfirmDeleteAttachment"
      button-label-confirm="Delete"
      :function-cancel="cancelRemoveAttachment"
      :function-confirm="confirmedRemoveAttachment"
      modal-header="Delete Attachment"
    >
      Are you sure you want to delete the <strong>'{{ displayName(existingAttachments, deleteAttachmentIndex) }}'</strong> attachment?
    </AreYouSureModal>
    <div v-if="isOpen">
      <ul class="pill-list pl-0 mt-3">
        <li
          v-for="(attachment, index) in existingAttachments"
          :id="`note-${note.id}-attachment-${index}`"
          :key="attachment.name"
          class="mt-2"
        >
          <span class="pill text-no-wrap">
            <a
              :id="`note-${note.id}-attachment-${index}`"
              :href="downloadUrl(attachment)"
            >
              <v-icon :icon="mdiPaperclip" />
              {{ attachment.displayName }}
            </a>
            <v-btn
              v-if="!note.legacySource && (currentUser.isAdmin || currentUser.uid === author.uid)"
              :id="`note-${note.id}-remove-note-attachment-${index}`"
              variant="text"
              class="p-0"
              @click.prevent="removeAttachmentByIndex(index)"
            >
              <v-icon
                :icon="mdiCloseCircleOutline"
                class="font-size-20 pl-2"
                color="error"
              />
              <span class="sr-only">Delete attachment '{{ attachment.displayName }}'</span>
            </v-btn>
          </span>
        </li>
      </ul>
      <div v-if="!note.legacySource && currentUser.uid === author.uid">
        <div v-if="attachmentError" class="mt-3 mb-3 w-100">
          <v-icon :icon="mdiAlertRhombus" class="text-danger pr-1" />
          <span :id="`note-${note.id}-attachment-error`" aria-live="polite" role="alert">{{ attachmentError }}</span>
        </div>
        <div v-if="uploadingAttachment" class="w-100">
          <v-icon :icon="mdiSync" spin /> Uploading {{ size(attachments) === 1 ? 'attachment' : 'attachments' }}...
        </div>
        <div v-if="size(existingAttachments) < contextStore.config.maxAttachmentsPerNote && !uploadingAttachment" class="w-100">
          <label for="choose-file-for-note-attachment" class="sr-only"><span class="sr-only">Note </span>Attachments</label>
          <div :id="`note-${note.id}-attachment-dropzone`" class="choose-attachment-file-wrapper pl-3 pr-3 text-no-wrap w-100">
            Add attachment:
            <v-btn
              id="choose-file-for-note-attachment"
              class="btn-file-upload mt-2 mb-2"
              color="primary"
              size="sm"
              type="file"
              variant="outlined"
              @keydown.enter.prevent="clickBrowseForAttachment"
            >
              Select File
            </v-btn>
            <v-file-input
              ref="attachment-file-input"
              v-model="attachments"
              density="comfortable"
              :disabled="size(existingAttachments) === contextStore.config.maxAttachmentsPerNote"
              flat
              hide-details
              multiple
              :prepend-icon="null"
              single-line
              variant="solo-filled"
            />
          </div>
        </div>
        <div v-if="size(existingAttachments) === contextStore.config.maxAttachmentsPerNote" :id="`note-${note.id}-max-attachments-notice`" class="w-100">
          A note can have no more than {{ contextStore.config.maxAttachmentsPerNote }} attachments.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import {addAttachments, removeAttachment} from '@/api/notes'
import {addFileDropEventListeners, validateAttachment} from '@/lib/note'
import {alertScreenReader, numFormat, oxfordJoin, toInt} from '@/lib/utils'
import {cloneDeep, each, get, isEmpty, isNil, map, orderBy, size} from 'lodash'
import {computed, onBeforeMount, reactive, ref, watch} from 'vue'
import {DateTime} from 'luxon'
import {getBoaUserRoles, termNameForSisId} from '@/berkeley'
import {getCalnetProfileByCsid, getCalnetProfileByUid} from '@/api/user'
import {mdiAlertRhombus, mdiCloseCircleOutline, mdiPaperclip, mdiSync} from '@mdi/js'
import {stripHtmlAndTrim} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  afterSaved: {
    required: true,
    type: Function
  },
  deleteNote: {
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

const clickBrowseForAttachment = () => document.getElementById('attachment-file-input').click()

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
          author.value.role = oxfordJoin(getBoaUserRoles(author.value, author.value.departments[0]))
        }
      }
      if (author_uid) {
        if (author_uid === currentUser.uid) {
          callback(currentUser)
        } else {
          getCalnetProfileByUid(author_uid).then(callback)
        }
      } else if (props.note.author.sid) {
        getCalnetProfileByCsid(props.note.author.sid).then(callback)
      }
    }
  }
}

const removeAttachmentByIndex = (index) => {
  clearErrors()
  const removeMe = existingAttachments.value[index]
  if (removeMe.id) {
    deleteAttachmentIndex.value = index
    showConfirmDeleteAttachment.value = true
  } else {
    existingAttachments.value.splice(index, 1)
  }
}

const cancelRemoveAttachment = () => {
  showConfirmDeleteAttachment.value = false
  deleteAttachmentIndex.value = null
}
const clearErrors = () => {
  attachmentError.value = null
}
const confirmedRemoveAttachment = () => {
  showConfirmDeleteAttachment.value = false
  const attachment = existingAttachments.value[deleteAttachmentIndex.value]
  if (attachment && attachment.id) {
    existingAttachments.value.splice(deleteAttachmentIndex.value, 1)
    return removeAttachment(props.note.id, attachment.id).then(updatedNote => {
      alertScreenReader(`Attachment '${attachment.displayName}' removed`)
      props.afterSaved(updatedNote)
    })
  }
}

const displayName = (attachments, index) => {
  return size(attachments) <= index ? '' : attachments[index].displayName
}

const downloadUrl = (attachment) => {
  return `${contextStore.config.apiBaseUrl}/api/notes/attachment/${attachment.id}`
}

const resetAttachments = () => {
  existingAttachments.value = cloneDeep(props.note.attachments)
}

const resetFileInput = () => {
  const element = document.getElementById('attachment-file-input')
  if (element) {
    element.reset()
  }
}

const attachmentError = ref(undefined)
const attachments = ref([])
const author = ref(get(props.note, 'author'))
const authorDepartments = computed(() => orderBy(map(author.value.departments, 'name')))
const contextStore = useContextStore()
const currentUser = reactive(contextStore.currentUser)
const deleteAttachmentIndex = ref(undefined)
const existingAttachments = ref(undefined)
const showConfirmDeleteAttachment = ref(false)
const uploadingAttachment = ref(false)

watch(attachments, files => {
  if (size(files)) {
    attachmentError.value = validateAttachment(files, existingAttachments.value)
    if (this.attachmentError) {
      resetFileInput()
    } else {
      clearErrors()
      each(files, attachment => {
        attachment.displayName = attachment.name
        alertScreenReader(`Uploading attachment '${attachment.displayName}'`)
      })
      uploadingAttachment.value = true
      addAttachments(props.note.id, files).then(updatedNote => {
        alertScreenReader(`${size(files)} ${size(files) === 1 ? 'attachment' : 'attachments'} added.`)
        props.afterSaved(updatedNote)
        resetAttachments()
        uploadingAttachment.value = false
      }).catch(error => {
        alertScreenReader()
        attachmentError.value = get(error, 'message')
        uploadingAttachment.value = false
        resetFileInput()
      })
    }
  }
})

watch(() => props.isOpen, () => {
  clearErrors()
  loadAuthorDetails()
})

watch(() => props.note, () => {
  resetAttachments()
  loadAuthorDetails()
})

watch(() => props.note.attachments, resetAttachments)

onBeforeMount(() => addFileDropEventListeners())

loadAuthorDetails()
resetAttachments()

</script>

<style scoped>
.advising-note-outer {
  flex-basis: 100%;
}
.note-snippet-when-closed {
  height: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
