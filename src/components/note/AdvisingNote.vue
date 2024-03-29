<template>
  <div :id="`note-${note.id}-outer`" class="advising-note-outer">
    <div :id="`note-${note.id}-is-closed`" :class="{'truncate-with-ellipsis': !isOpen}" aria-label="Advising note">
      <span v-if="note.isDraft" :id="`note-${note.id}-is-draft`">
        <span class="pr-2">
          <b-badge pill variant="danger">Draft</b-badge>
        </span>
        <span :id="`note-${note.id}-subject`">{{ note.subject || config.draftNoteSubjectPlaceholder }}</span>
      </span>
      <span v-if="!note.isDraft">
        <span v-if="note.subject" :id="`note-${note.id}-subject`">{{ note.subject }}</span>
        <span v-if="!note.subject && size(note.message)" :id="`note-${note.id}-subject`" v-html="note.message"></span>
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
      <div v-if="isEditable">
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
            <dd>{{ DateTime.fromJSDate(note.createdAt).toFormat('MM/DD/YYYY') }}</dd>
          </div>
          <div>
            <dt>Form Status </dt>
            <dd>{{ note.eForm.status }}</dd>
          </div>
          <div>
            <dt>Final Date &amp; Time Stamp</dt>
            <dd>{{ DateTime.fromJSDate(note.updatedAt).toFormat('MM/DD/YYYY h:mm:ssa') }}</dd>
          </div>
        </dl>
      </div>
      <div v-if="!isNil(author) && !author.name && !author.email && !note.eForm" class="mt-2 text-black-50 advisor-profile-not-found">
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
        <div class="pill-list-header mt-3 mb-1">{{ size(note.topics) === 1 ? 'Topic Category' : 'Topic Categories' }}</div>
        <ul class="pill-list pl-0">
          <li
            v-for="(topic, index) in note.topics"
            :id="`note-${note.id}-topic-${index}`"
            :key="topic"
            class="mt-2"
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
      v-if="showConfirmDeleteAttachment"
      :function-cancel="cancelRemoveAttachment"
      :function-confirm="confirmedRemoveAttachment"
      :show-modal="showConfirmDeleteAttachment"
      button-label-confirm="Delete"
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
          <span class="pill pill-attachment text-no-wrap">
            <a
              :id="`note-${note.id}-attachment-${index}`"
              :href="downloadUrl(attachment)"
            >
              <v-icon :icon="mdiPaperclip" />
              {{ attachment.displayName }}
            </a>
            <v-btn
              v-if="isEditable && (currentUser.isAdmin || currentUser.uid === author.uid)"
              :id="`note-${note.id}-remove-note-attachment-${index}`"
              variant="link"
              class="p-0"
              @click.prevent="removeAttachment(index)"
            >
              <v-icon :icon="mdiCloseCircleOutline" class="font-size-20 has-error pl-2" />
              <span class="sr-only">Delete attachment '{{ attachment.displayName }}'</span>
            </v-btn>
          </span>
        </li>
      </ul>
      <div v-if="isEditable && currentUser.uid === author.uid">
        <div v-if="attachmentError" class="mt-3 mb-3 w-100">
          <v-icon :icon="mdiAlertRhombus" class="text-danger pr-1" />
          <span :id="`note-${note.id}-attachment-error`" aria-live="polite" role="alert">{{ attachmentError }}</span>
        </div>
        <div v-if="uploadingAttachment" class="w-100">
          <v-icon :icon="mdiSync" spin /> Uploading {{ size(attachments) === 1 ? 'attachment' : 'attachments' }}...
        </div>
        <div v-if="size(existingAttachments) < config.maxAttachmentsPerNote && !uploadingAttachment" class="w-100">
          <label for="choose-file-for-note-attachment" class="sr-only"><span class="sr-only">Note </span>Attachments</label>
          <div :id="`note-${note.id}-attachment-dropzone`" class="choose-attachment-file-wrapper no-wrap pl-3 pr-3 w-100">
            Add attachment:
            <v-btn
              id="choose-file-for-note-attachment"
              type="file"
              variant="outline-primary"
              class="btn-file-upload mt-2 mb-2"
              size="sm"
              @keydown.enter.prevent="clickBrowseForAttachment"
            >
              Select File
            </v-btn>
            <b-form-file
              ref="attachment-file-input"
              v-model="attachments"
              :disabled="size(existingAttachments) === config.maxAttachmentsPerNote"
              :state="Boolean(attachments && attachments.length)"
              :multiple="true"
              :plain="true"
            ></b-form-file>
          </div>
        </div>
        <div v-if="size(existingAttachments) === config.maxAttachmentsPerNote" :id="`note-${note.id}-max-attachments-notice`" class="w-100">
          A note can have no more than {{ config.maxAttachmentsPerNote }} attachments.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {mdiAlertRhombus, mdiCloseCircleOutline, mdiPaperclip, mdiSync} from '@mdi/js'
</script>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import {addAttachments, removeAttachment} from '@/api/notes'
import {addFileDropEventListeners, validateAttachment} from '@/lib/note'
import {cloneDeep, each, get, isEmpty, isNil, map, orderBy, size} from 'lodash'
import {DateTime} from 'luxon'
import {getBoaUserRoles, termNameForSisId} from '@/berkeley'
import {getCalnetProfileByCsid, getCalnetProfileByUid} from '@/api/user'
import {numFormat, oxfordJoin, toInt} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

export default {
  name: 'AdvisingNote',
  components: {AreYouSureModal},
  props: {
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
  },
  data: () => ({
    allUsers: undefined,
    attachmentError: undefined,
    attachments: [],
    author: undefined,
    deleteAttachmentIndex: undefined,
    deleteAttachmentIds: [],
    existingAttachments: undefined,
    showConfirmDeleteAttachment: false,
    uploadingAttachment: false
  }),
  computed: {
    authorDepartments() {
      return orderBy(map(this.author.departments, 'name'))
    },
    isEditable() {
      return !this.note.legacySource
    },
    noteAttachments() {
      return this.note.attachments
    }
  },
  watch: {
    attachments(files) {
      if (size(files)) {
        this.attachmentError = validateAttachment(files, this.existingAttachments)
        if (this.attachmentError) {
          this.resetFileInput()
        } else {
          this.clearErrors()
          each(files, attachment => {
            attachment.displayName = attachment.name
            useContextStore().alertScreenReader(`Uploading attachment '${attachment.displayName}'`)
          })
          this.uploadingAttachment = true
          addAttachments(this.note.id, files).then(updatedNote => {
            useContextStore().alertScreenReader(`${size(files)} ${size(files) === 1 ? 'attachment' : 'attachments'} added.`)
            this.afterSaved(updatedNote)
            this.resetAttachments()
            this.uploadingAttachment = false
          })
            .catch(error => {
              useContextStore().alertScreenReader()
              this.attachmentError = get(error, 'message')
              this.uploadingAttachment = false
              this.resetFileInput()
            })
        }
      }
    },
    isOpen() {
      this.clearErrors()
      this.loadAuthorDetails()
    },
    note() {
      this.resetAttachments()
      this.loadAuthorDetails()
    },
    noteAttachments() {
      this.resetAttachments()
    }
  },
  beforeCreate() {
    addFileDropEventListeners()
  },
  created() {
    this.author = get(this.note, 'author')
    this.loadAuthorDetails()
    this.resetAttachments()
  },
  methods: {
    clickBrowseForAttachment() {
      this.$refs['attachment-file-input'].$el.click()
    },
    loadAuthorDetails() {
      const requiresLazyLoad = (
        this.isOpen &&
        (
          !get(this.note, 'author.name') ||
          !get(this.note, 'author.role') ||
          get(this.author, 'uid') !== get(this.note, 'author.uid') ||
          get(this.author, 'sid') !== get(this.note, 'author.sid')
        )
      )
      if (requiresLazyLoad) {
        const hasIdentifier = get(this.note, 'author.uid') || get(this.note, 'author.sid')
        if (hasIdentifier) {
          const author_uid = this.note.author.uid
          const callback = data => {
            this.author = data
            this.author.role = this.author.role || this.author.title
            if (!this.author.role && this.author.departments.length) {
              this.author.role = oxfordJoin(getBoaUserRoles(this.author, this.author.departments[0]))
            }
          }
          if (author_uid) {
            if (author_uid === this.currentUser.uid) {
              callback(this.currentUser)
            } else {
              getCalnetProfileByUid(author_uid).then(callback)
            }
          } else if (this.note.author.sid) {
            getCalnetProfileByCsid(this.note.author.sid).then(callback)
          }
        }
      }
    },
    removeAttachment(index) {
      this.clearErrors()
      const removeMe = this.existingAttachments[index]
      if (removeMe.id) {
        this.deleteAttachmentIndex = index
        this.showConfirmDeleteAttachment = true
      } else {
        this.existingAttachments.splice(index, 1)
      }
    },
    cancelRemoveAttachment() {
      this.showConfirmDeleteAttachment = false
      this.deleteAttachmentIndex = null
    },
    clearErrors() {
      this.attachmentError = null
    },
    confirmedRemoveAttachment() {
      this.showConfirmDeleteAttachment = false
      const attachment = this.existingAttachments[this.deleteAttachmentIndex]
      if (attachment && attachment.id) {
        this.existingAttachments.splice(this.deleteAttachmentIndex, 1)
        return removeAttachment(this.note.id, attachment.id).then(updatedNote => {
          useContextStore().alertScreenReader(`Attachment '${attachment.displayName}' removed`)
          this.afterSaved(updatedNote)
        })
      }
    },
    displayName(attachments, index) {
      return size(attachments) <= index ? '' : attachments[index].displayName
    },
    downloadUrl(attachment) {
      return `${this.config.apiBaseUrl}/api/notes/attachment/${attachment.id}`
    },
    isNil,
    numFormat,
    oxfordJoin,
    resetAttachments() {
      this.existingAttachments = cloneDeep(this.note.attachments)
    },
    resetFileInput() {
      const inputElement = this.$refs['attachment-file-input']
      if (inputElement) {
        inputElement.reset()
      }
    },
    size,
    termNameForSisId,
    toInt
  }
}
</script>

<style scoped>
.advising-note-outer {
  flex-basis: 100%;
}
.advisor-profile-not-found {
  font-size: 14px;
}
</style>
