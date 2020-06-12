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
      <div v-if="!isNil(note.author) && !note.author.name && !note.author.email" class="mt-2 advisor-profile-not-found">
        Advisor profile not found
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
        </div>
        <div v-if="size(note.author.departments)" class="text-secondary">
          <div v-for="(deptName, index) in orderBy(map(note.author.departments, 'name'))" :key="index">
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
      :modal-body="`Are you sure you want to delete the <b>'${displayName(attachments, deleteAttachmentIndex)}'</b> attachment?`"
      :show-modal="showConfirmDeleteAttachment"
      button-label-confirm="Delete"
      modal-header="Delete Attachment" />
    <div>
      <ul class="pill-list pl-0 mt-3">
        <li
          v-for="(attachment, index) in attachments"
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
          <font-awesome icon="sync" spin /> Uploading attachment...
        </div>
        <div v-if="size(attachments) < $config.maxAttachmentsPerNote && !uploadingAttachment" class="w-100">
          <label for="choose-file-for-note-attachment" class="sr-only"><span class="sr-only">Note </span>Attachments</label>
          <div :id="`note-${note.id}-attachment-dropzone`" class="choose-attachment-file-wrapper no-wrap pl-3 pr-3 w-100">
            Drop file to upload attachment or
            <b-btn
              id="choose-file-for-note-attachment"
              type="file"
              variant="outline-primary"
              class="btn-file-upload mt-2 mb-2"
              size="sm"
              @keydown.enter.prevent="clickBrowseForAttachment">
              Browse<span class="sr-only"> for file to upload</span>
            </b-btn>
            <b-form-file
              ref="attachment-file-input"
              v-model="attachment"
              :disabled="size(attachments) === $config.maxAttachmentsPerNote"
              :state="Boolean(attachment)"
              :plain="true"
            ></b-form-file>
          </div>
        </div>
        <div v-if="size(attachments) === $config.maxAttachmentsPerNote" :id="`note-${note.id}-max-attachments-notice`" class="w-100">
          A note can have no more than {{ $config.maxAttachmentsPerNote }} attachments.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal';
import Attachments from '@/mixins/Attachments';
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';
import { addAttachment, removeAttachment } from '@/api/notes';
import { getCalnetProfileByCsid, getCalnetProfileByUid } from '@/api/user';

export default {
  name: 'AdvisingNote',
  components: { AreYouSureModal },
  mixins: [Attachments, Context, Util],
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
    deleteAttachmentIndex: undefined,
    deleteAttachmentIds: [],
    showConfirmDeleteAttachment: false,
    uploadingAttachment: false
  }),
  computed: {
    isEditable() {
      return !this.note.isLegacy;
    }
  },
  watch: {
    attachment(file) {
      if (file) {
        this.attachmentError = this.validateAttachment(file, this.attachments);
        if (this.attachmentError) {
          this.attachment = null;
          this.resetFileInput();
        } else {
          this.clearErrors();
          this.attachment = file;
          this.attachment.displayName = file.name;
          this.alertScreenReader(`Uploading attachment '${this.attachment.displayName}'`);
          this.uploadingAttachment = true;
          addAttachment(this.note.id, this.attachment).then(updatedNote => {
            this.alertScreenReader(`Attachment '${this.attachment.displayName}' added`);
            this.uploadingAttachment = false;
            this.afterSaved(updatedNote);
            this.resetAttachments();
            this.resetFileInput();
          });
        }
      }
    },
    isOpen() {
      this.clearErrors();
      this.setAuthor();
    },
    note() {
      this.resetAttachments();
    }
  },
  created() {
    this.setAuthor();
    this.resetAttachments();
  },
  methods: {
    setAuthor() {
      const requiresLazyLoad = this.isOpen && (!this.get(this.note, 'author.name') || !this.get(this.note, 'author.role'));
      if (requiresLazyLoad) {
        const hasIdentifier = this.get(this.note, 'author.uid') || this.get(this.note, 'author.sid');
        if (hasIdentifier) {
          const author_uid = this.note.author.uid;
          if (author_uid) {
            if (author_uid === this.$currentUser.uid) {
              this.note.author = this.$currentUser;
            } else {
              getCalnetProfileByUid(author_uid).then(data => {
                this.note.author = data;
              });
            }
          } else if (this.note.author.sid) {
            getCalnetProfileByCsid(this.note.author.sid).then(data => {
              this.note.author = data;
            });
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
      return `${this.$config.apiBaseUrl}/api/notes/attachment/${attachment.id}`;
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
.advisor-profile-not-found {
  color: #999;
  font-size: 14px;
}
</style>
