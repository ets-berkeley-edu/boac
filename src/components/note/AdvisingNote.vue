<template>
  <div :id="`note-${note.id}-outer`" class="advising-note-outer">
    <div :id="`note-${note.id}-is-closed`" :class="{'truncate-with-ellipsis': !isOpen}" aria-label="Advising note">
      <span v-if="note.subject" :id="`note-${note.id}-subject`">{{ note.subject }}</span>
      <span v-if="!note.subject && size(note.message)" :id="`note-${note.id}-subject`" v-html="note.message"></span>
      <span v-if="!note.subject && !size(note.message) && note.category" :id="`note-${note.id}-subject`">{{ note.category }}<span v-if="note.subcategory">, {{ note.subcategory }}</span></span>
      <span v-if="!note.subject && !size(note.message) && !note.category" :id="`note-${note.id}-category-closed`">{{ note.author.departments && note.author.departments[0].name }}
        advisor {{ note.author.name }}<span v-if="note.topics && size(note.topics)">: {{ oxfordJoin(note.topics) }}</span>
      </span>
    </div>
    <div v-if="isOpen" :id="`note-${note.id}-is-open`">
      <div v-if="isEditable">
        <b-btn
          v-if="$currentUser.isAdmin"
          :id="`btn-delete-note-${note.id}`"
          class="sr-only"
          @click.stop="deleteNote(note)">
          Delete Note
        </b-btn>
        <b-btn
          v-if="$currentUser.uid === note.author.uid"
          :id="`btn-edit-note-${note.id}`"
          class="sr-only"
          @click.stop="editNote(note)">
          Edit Note
        </b-btn>
      </div>
      <div v-if="note.subject && note.message" class="mt-2">
        <span :id="`note-${note.id}-message-open`" v-html="note.message"></span>
      </div>
      <div v-if="!isNil(note.author) && !note.author.name && !note.author.email" class="mt-2 text-black-50 advisor-profile-not-found">
        Advisor profile not found
        <span v-if="note.legacySource" class="font-italic">
          (note imported from {{ note.legacySource }})
        </span>
      </div>
      <div v-if="note.author" class="mt-2">
        <div v-if="note.author.name || note.author.email">
          <span class="sr-only">Note created by </span>
          <a
            v-if="note.author.uid && note.author.name"
            :id="`note-${note.id}-author-name`"
            :aria-label="`Open UC Berkeley Directory page of ${note.author.name} in a new window`"
            :href="`https://www.berkeley.edu/directory/results?search-term=${note.author.name}`"
            target="_blank">{{ note.author.name }}</a>
          <span v-if="!note.author.uid && note.author.name" :id="`note-${note.id}-author-name`">
            {{ note.author.name }}
          </span>
          <span v-if="!note.author.uid && !note.author.name && note.author.email" :id="`note-${note.id}-author-email`">
            {{ note.author.email }}
          </span>
          <span v-if="note.author.role || note.author.title">
            - <span :id="`note-${note.id}-author-role`" class="text-dark">{{ note.author.role || note.author.title }}</span>
          </span>
          <span v-if="note.legacySource" class="font-italic text-black-50">
            (note imported from {{ note.legacySource }})
          </span>
        </div>
        <div v-if="size(note.author.departments)" class="text-secondary">
          <div v-for="(deptName, index) in $_.orderBy(map(note.author.departments, 'name'))" :key="index">
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
            class="mt-2">
            <span class="pill pill-attachment text-uppercase text-nowrap">{{ topic }}</span>
          </li>
        </ul>
      </div>
    </div>
    <AreYouSureModal
      v-if="showConfirmDeleteAttachment"
      :function-cancel="cancelRemoveAttachment"
      :function-confirm="confirmedRemoveAttachment"
      :modal-body="`Are you sure you want to delete the <b>'${displayName(existingAttachments, deleteAttachmentIndex)}'</b> attachment?`"
      :show-modal="showConfirmDeleteAttachment"
      button-label-confirm="Delete"
      modal-header="Delete Attachment" />
    <div v-if="isOpen">
      <ul class="pill-list pl-0 mt-3">
        <li
          v-for="(attachment, index) in existingAttachments"
          :id="`note-${note.id}-attachment-${index}`"
          :key="attachment.name"
          class="mt-2">
          <span class="pill pill-attachment text-nowrap">
            <a
              :id="`note-${note.id}-attachment-${index}`"
              :href="downloadUrl(attachment)">
              <font-awesome icon="paperclip" />
              {{ attachment.displayName }}
            </a>
            <b-btn
              v-if="isEditable && ($currentUser.isAdmin || $currentUser.uid === note.author.uid)"
              :id="`note-${note.id}-remove-note-attachment-${index}`"
              variant="link"
              class="p-0"
              @click.prevent="removeAttachment(index)">
              <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
              <span class="sr-only">Delete attachment '{{ attachment.displayName }}'</span>
            </b-btn>
          </span>
        </li>
      </ul>
      <div v-if="isEditable && $currentUser.uid === note.author.uid">
        <div v-if="attachmentError" class="mt-3 mb-3 w-100">
          <font-awesome icon="exclamation-triangle" class="text-danger pr-1" />
          <span :id="`note-${note.id}-attachment-error`" aria-live="polite" role="alert">{{ attachmentError }}</span>
        </div>
        <div v-if="uploadingAttachment" class="w-100">
          <font-awesome icon="sync" spin /> Uploading {{ size(attachments) === 1 ? 'attachment' : 'attachments' }}...
        </div>
        <div v-if="size(existingAttachments) < $config.maxAttachmentsPerNote && !uploadingAttachment" class="w-100">
          <label for="choose-file-for-note-attachment" class="sr-only"><span class="sr-only">Note </span>Attachments</label>
          <div :id="`note-${note.id}-attachment-dropzone`" class="choose-attachment-file-wrapper no-wrap pl-3 pr-3 w-100">
            Add attachment:
            <b-btn
              id="choose-file-for-note-attachment"
              type="file"
              variant="outline-primary"
              class="btn-file-upload mt-2 mb-2"
              size="sm"
              @keydown.enter.prevent="clickBrowseForAttachment">
              Select File
            </b-btn>
            <b-form-file
              ref="attachment-file-input"
              v-model="attachments"
              :disabled="size(existingAttachments) === $config.maxAttachmentsPerNote"
              :state="Boolean(attachments && attachments.length)"
              :multiple="true"
              :plain="true"
            ></b-form-file>
          </div>
        </div>
        <div v-if="size(existingAttachments) === $config.maxAttachmentsPerNote" :id="`note-${note.id}-max-attachments-notice`" class="w-100">
          A note can have no more than {{ $config.maxAttachmentsPerNote }} attachments.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Attachments from '@/mixins/Attachments'
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import { addAttachments, removeAttachment } from '@/api/notes'
import { getCalnetProfileByCsid, getCalnetProfileByUid } from '@/api/user'

export default {
  name: 'AdvisingNote',
  components: { AreYouSureModal },
  mixins: [Attachments, Context, Util],
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
    isOpen: Boolean,
    note: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    allUsers: undefined,
    attachmentError: undefined,
    attachments: [],
    deleteAttachmentIndex: undefined,
    deleteAttachmentIds: [],
    existingAttachments: undefined,
    showConfirmDeleteAttachment: false,
    uploadingAttachment: false
  }),
  computed: {
    isEditable() {
      return !this.note.legacySource
    }
  },
  watch: {
    attachments(files) {
      if (this.size(files)) {
        this.attachmentError = this.validateAttachment(files, this.existingAttachments)
        if (this.attachmentError) {
          this.resetFileInput()
        } else {
          this.clearErrors()
          this.$_.each(files, attachment => {
            attachment.displayName = attachment.name
            this.alertScreenReader(`Uploading attachment '${attachment.displayName}'`)
          })
          this.uploadingAttachment = true
          addAttachments(this.note.id, files).then(updatedNote => {
            this.alertScreenReader(`${this.size(files)} ${this.size(files) === 1 ? 'attachment' : 'attachments'} added.`)
            this.afterSaved(updatedNote)
            this.resetAttachments()
            this.uploadingAttachment = false
          })
            .catch(error => {
              this.alertScreenReader()
              this.attachmentError = this.$_.get(error, 'message')
              this.uploadingAttachment = false
              this.resetFileInput()
            })
        }
      }
    },
    isOpen() {
      this.clearErrors()
      this.setAuthor()
    },
    note() {
      this.resetAttachments()
    }
  },
  created() {
    this.setAuthor()
    this.resetAttachments()
  },
  methods: {
    setAuthor() {
      const requiresLazyLoad = this.isOpen && (!this.$_.get(this.note, 'author.name') || !this.$_.get(this.note, 'author.role'))
      if (requiresLazyLoad) {
        const hasIdentifier = this.$_.get(this.note, 'author.uid') || this.$_.get(this.note, 'author.sid')
        if (hasIdentifier) {
          const author_uid = this.note.author.uid
          if (author_uid) {
            if (author_uid === this.$currentUser.uid) {
              // TODO: do not mutate prop
              this.note.author = this.$currentUser  // eslint-disable-line vue/no-mutating-props
            } else {
              getCalnetProfileByUid(author_uid).then(data => {
                // TODO: do not mutate prop
                this.note.author = data  // eslint-disable-line vue/no-mutating-props
              })
            }
          } else if (this.note.author.sid) {
            getCalnetProfileByCsid(this.note.author.sid).then(data => {
              // TODO: do not mutate prop
              this.note.author = data  // eslint-disable-line vue/no-mutating-props
            })
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
      this.existingAttachments.splice(this.deleteAttachmentIndex, 1)
      removeAttachment(this.note.id, attachment.id).then(updatedNote => {
        this.alertScreenReader(`Attachment '${attachment.displayName}' removed`)
        this.afterSaved(updatedNote)
      })
    },
    displayName(attachments, index) {
      return this.size(attachments) <= index ? '' : attachments[index].displayName
    },
    downloadUrl(attachment) {
      return `${this.$config.apiBaseUrl}/api/notes/attachment/${attachment.id}`
    },
    resetAttachments() {
      this.existingAttachments = this.$_.cloneDeep(this.note.attachments)
    },
    resetFileInput() {
      const inputElement = this.$refs['attachment-file-input']
      if (inputElement) {
        inputElement.reset()
      }
    }
  },
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
