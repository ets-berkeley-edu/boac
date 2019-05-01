<template>
  <div :id="`note-${note.id}-outer`" class="advising-note-outer">
    <div :id="`note-${note.id}-is-closed`" :class="{'truncate': !isOpen}">
      <span v-if="note.subject" :id="`note-${note.id}-subject-closed`">{{ note.subject }}</span>
      <span v-if="!note.subject && size(note.message)" :id="`note-${note.id}-message-closed`" v-html="note.message"></span>
      <span v-if="!note.subject && !size(note.message)" :id="`note-${note.id}-category-closed`">{{ note.category }}<span v-if="note.subcategory" :id="`note-${note.id}-subcategory-closed`">, {{ note.subcategory }}</span></span>
    </div>
    <div v-if="isOpen" :id="`note-${note.id}-is-open`">
      <div v-if="featureFlagEditNotes">
        <b-btn
          v-if="user.isAdmin"
          class="sr-only"
          @click.stop="deleteNote(note)">
          Delete Note
        </b-btn>
        <b-btn
          v-if="user.uid === note.author.uid"
          class="sr-only"
          @click.stop="editNote(note)">
          Edit Note
        </b-btn>
      </div>
      <div v-if="note.subject && note.message" class="mt-2">
        <span :id="`note-${note.id}-message-open`" v-html="note.message"></span>
      </div>
      <div v-if="!isUndefined(author) && !author.name" class="mt-2 advisor-profile-not-found">
        Advisor profile not found
      </div>
      <div v-if="author" class="mt-2">
        <div v-if="author.name">
          <a
            :id="`note-${note.id}-author-name`"
            :aria-label="`Open UC Berkeley Directory page of ${author.name} in a new window`"
            :href="`https://www.berkeley.edu/directory/results?search-term=${author.name}`"
            target="_blank">{{ author.name }}</a>
          <span v-if="author.role">
            - <span :id="`note-${note.id}-author-role`" class="text-dark">{{ author.role }}</span>
          </span>
        </div>
        <div v-if="size(author.departments)" class="text-secondary">
          <span v-if="note.isLegacy">(currently </span><span v-if="author.title">{{ author.title }}, </span><span v-for="(dept, index) in author.departments" :key="dept.code">
            <span :id="`note-${note.id}-author-dept-${index}`">{{ dept.name }}</span>
          </span><span v-if="note.isLegacy">)</span>
        </div>
      </div>
      <div v-if="size(note.topics)">
        <div class="pill-list-header mt-3 mb-1">{{ size(note.topics) === 1 ? 'Topic Category' : 'Topic Categories' }}</div>
        <ul class="pill-list pl-0">
          <li
            v-for="(topic, index) in note.topics"
            :id="`note-${note.id}-topic-${index}`"
            :key="topic"
            class="mt-2">
            <span class="pill text-uppercase text-nowrap">{{ topic }}</span>
          </li>
        </ul>
      </div>
    </div>
    <AreYouSureModal
      v-if="showConfirmDeleteAttachment"
      button-label-confirm="Delete"
      :function-cancel="cancelRemoveAttachment"
      :function-confirm="confirmedRemoveAttachment"
      :modal-body="`Are you sure you want to delete the <b>'${displayName(attachments, deleteAttachmentIndex)}'</b> attachment?`"
      modal-header="Delete Attachment"
      :show-modal="showConfirmDeleteAttachment" />
    <div>
      <ul class="pill-list pl-0 mt-3">
        <li
          v-for="(attachment, index) in attachments"
          :id="`note-${note.id}-attachment-${index}`"
          :key="attachment.name"
          class="mt-2">
          <span class="pill pill-attachment text-nowrap">
            <a
              v-if="!isPreCsNote"
              :id="`note-${note.id}-attachment-${index}`"
              :href="downloadUrl(attachment)">
              <i class="fas fa-paperclip"></i>
              {{ attachment.displayName }}
            </a>
            <b-btn
              v-if="featureFlagEditNotes && (user.isAdmin || user.uid === note.author.uid)"
              :id="`note-${note.id}-remove-note-attachment-${index}`"
              variant="link"
              class="p-0"
              @click.prevent="removeAttachment(index)">
              <i class="fas fa-times-circle has-error pl-2"></i>
            </b-btn>
            <span
              v-if="isPreCsNote"
              :id="`note-${note.id}-attachment-${index}`">
              <i class="fas fa-paperclip"></i> {{ attachment.displayName }}
            </span>
          </span>
        </li>
      </ul>
      <div v-if="featureFlagEditNotes && user.uid === note.author.uid">
        <div v-if="attachmentError" class="mt-3 mb-3 w-100">
          <i class="fa fa-exclamation-triangle text-danger pr-1"></i>
          <span :id="`note-${note.id}-attachment-error`" aria-live="polite" role="alert">{{ attachmentError }}</span>
        </div>
        <div v-if="uploadingAttachment" class="w-100">
          <i class="fas fa-spin fa-sync"></i> Uploading attachment...
        </div>
        <div v-if="size(attachments) < maxAttachmentsPerNote && !uploadingAttachment" class="w-100">
          <label for="choose-file-for-note-attachment" class="sr-only"><span class="sr-only">Note </span>Attachments</label>
          <div :id="`note-${note.id}-attachment-dropzone`" class="choose-attachment-file-wrapper no-wrap pl-3 pr-3 w-100">
            Drop file to upload attachment or
            <b-btn
              id="choose-file-for-note-attachment"
              type="file"
              variant="outline-primary"
              class="btn-file-upload mt-2 mb-2"
              size="sm"
              @keydown.enter.prevent="triggerFileInput">
              Browse<span class="sr-only"> for file to upload</span>
            </b-btn>
            <b-form-file
              ref="attachment-file-input"
              v-model="attachment"
              :disabled="size(attachments) === maxAttachmentsPerNote"
              :state="Boolean(attachment)"
              :plain="true"
            ></b-form-file>
          </div>
        </div>
        <div v-if="size(attachments) === maxAttachmentsPerNote" :id="`note-${note.id}-max-attachments-notice`" class="w-100">
          A note can have no more than {{ maxAttachmentsPerNote }} attachments.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import store from '@/store';
import AreYouSureModal from '@/components/util/AreYouSureModal';
import Context from '@/mixins/Context';
import NoteUtil from '@/components/note/NoteUtil';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { addAttachment, removeAttachment } from '@/api/notes';
import { getUserByUid } from '@/api/user';

export default {
  name: 'AdvisingNote',
  components: { AreYouSureModal },
  mixins: [Context, NoteUtil, UserMetadata, Util],
  props: {
    afterSaved: Function,
    deleteNote: Function,
    editNote: Function,
    isOpen: Boolean,
    note: Object
  },
  data: () => ({
    allUsers: undefined,
    attachment: undefined,
    attachmentError: undefined,
    attachments: undefined,
    author: undefined,
    deleteAttachmentIndex: undefined,
    deleteAttachmentIds: [],
    showConfirmDeleteAttachment: false,
    uploadingAttachment: false
  }),
  computed: {
    isPreCsNote() {
      return this.get(this.note, 'createdBy') === 'UCBCONVERSION';
    }
  },
  watch: {
    attachment() {
      if (this.validateAttachment()) {
        this.alertScreenReader(`Uploading attachment '${this.attachment.displayName}'`);
        this.uploadingAttachment = true;
        addAttachment(this.note.id, this.attachment).then(updatedNote => {
          this.alertScreenReader(`Attachment '${this.attachment.displayName}' added`);
          this.uploadingAttachment = false;
          this.afterSaved(updatedNote);
          this.resetAttachments();
          this.resetFileInput();
        });
      } else {
        this.resetFileInput();
      }
    },
    isOpen() {
      this.setAuthor();
    },
    note() {
      this.resetAttachments();
    }
  },
  created() {
    this.setAuthor();
    this.initFileDropPrevention();
    this.resetAttachments();
  },
  methods: {
    setAuthor() {
      if (this.isOpen && this.isUndefined(this.author)) {
        if (this.note.author.name) {
          this.author = this.note.author;
        } else {
          const author_uid = this.note.author.uid;
          if (author_uid) {
            if (author_uid === this.user.uid) {
              this.author = this.user;
            } else {
              getUserByUid(author_uid).then(data => {
                this.author = data;
              });
            }
          } else if (this.note.author.sid) {
            store.dispatch('user/loadCalnetUserByCsid', this.note.author.sid).then(data => {
              this.author = data;
            });
          } else {
            this.author = null;
          }
        }
      }
    },
    removeAttachment(index) {
      this.clearErrors();
      const removeMe = this.attachments[index];
      if (removeMe.id) {
        this.deleteAttachmentIndex = index;
        this.showConfirmDeleteAttachment = true;
      } else {
        this.attachments.splice(index, 1);
      }
    },
    cancelRemoveAttachment() {
      this.showConfirmDeleteAttachment = false;
      this.deleteAttachmentIndex = null;
    },
    clearErrors() {
      this.attachmentError = null;
    },
    confirmedRemoveAttachment() {
      this.showConfirmDeleteAttachment = false;
      const attachment = this.attachments[this.deleteAttachmentIndex];
      this.attachments.splice(this.deleteAttachmentIndex, 1);
      removeAttachment(this.note.id, attachment.id).then(updatedNote => {
        this.alertScreenReader(`Attachment '${attachment.displayName}' removed`);
        this.afterSaved(updatedNote);
      });
    },
    displayName(attachments, index) {
      return this.size(attachments) <= index ? '' : attachments[index].displayName;
    },
    downloadUrl(attachment) {
      return this.apiBaseUrl + '/api/notes/attachment/' + attachment.id;
    },
    resetAttachments() {
      this.attachments = this.cloneDeep(this.note.attachments);
    },
    resetFileInput() {
      const inputElement = this.$refs['attachment-file-input'];
      if (inputElement) {
        inputElement.reset();
      }
    }
  },
}
</script>

<style scoped>
.advising-note-outer {
  flex-basis: 100%;
}
.btn-file-upload {
  border-color: grey;
  color: grey;
}
.btn-file-upload:hover,
.btn-file-upload:focus,
.btn-file-upload:active
{
  color: #333;
  background-color: #aaa;
}
.choose-attachment-file-wrapper {
  position: relative;
  align-items: center;
  overflow: hidden;
  display: inline-block;
  background-color: #f7f7f7;
  border: 1px solid #E0E0E0;
  border-radius: 4px;
  text-align: center;
}
.choose-attachment-file-wrapper input[type=file] {
  font-size: 100px;
  position: absolute;
  left: 0;
  top: 0;
  opacity: 0;
}
.choose-attachment-file-wrapper:hover,
.choose-attachment-file-wrapper:focus,
.choose-attachment-file-wrapper:active
{
  color: #333;
  background-color: #eee;
}
.form-control-file {
  height: 100%;
}
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.advisor-profile-not-found {
  color: #999;
  font-size: 14px;
}
</style>
