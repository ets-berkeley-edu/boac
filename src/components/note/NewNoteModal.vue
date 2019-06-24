<template>
  <div>
    <div :class="{'d-flex justify-content-center pl-3 pr-3': initialMode === 'batch'}">
      <b-btn
        id="new-note-button"
        class="mt-1 mr-2 btn-primary-color-override"
        :class="{'w-100': initialMode === 'batch'}"
        variant="primary"
        :disabled="disable"
        @click="openNewNoteModal()">
        <span class="m-1">
          <font-awesome icon="file-alt" />
          New Note
        </span>
      </b-btn>
    </div>
    <FocusLock
      v-if="!disable"
      :disabled="!undocked || showDiscardModal"
      :class="{'modal-full-screen': undocked}">
      <div
        id="new-note-modal-container"
        :class="{
          'd-none': isNil(newNoteMode),
          'modal-open': newNoteMode === 'docked',
          'modal-open modal-minimized': newNoteMode === 'minimized',
          'modal-open modal-saving': newNoteMode === 'saving',
          'modal-full-screen-content': undocked,
          'mt-4': initialMode === 'batch'
        }">
        <form @submit.prevent="create()">
          <div class="d-flex align-items-end pt-2 mb-1" :class="{'mt-2': undocked}">
            <div class="flex-grow-1 new-note-header font-weight-bolder">
              New Note
            </div>
            <div v-if="!undocked" class="pr-0">
              <label id="minimize-button-label" class="sr-only">Minimize the create note dialog box</label>
              <b-btn
                id="minimize-new-note-modal"
                variant="link"
                aria-labelledby="minimize-button-label"
                class="pr-2"
                @click.prevent="minimize()">
                <span class="sr-only">Minimize</span>
                <font-awesome icon="window-minimize" class="minimize-icon text-dark" />
              </b-btn>
            </div>
            <div v-if="!undocked" class="pr-2">
              <label id="cancel-button-label" class="sr-only">Cancel the create-note form</label>
              <b-btn
                id="cancel-new-note-modal"
                variant="link"
                aria-labelledby="cancel-button-label"
                class="pl-1 pb-1"
                @click.prevent="cancel()">
                <span class="sr-only">Cancel</span>
                <font-awesome icon="times" class="fa-icon-size text-dark" />
              </b-btn>
            </div>
          </div>
          <hr class="m-0" />
          <div class="mt-2 mr-3 mb-1 ml-3">
            <div v-if="newNoteMode === 'batch'">
              <div>
                <span
                  v-if="targetStudentCount"
                  class="font-italic"
                  :class="{'has-error': targetStudentCount >= 250, 'font-weight-bolder': targetStudentCount >= 500}">
                  Note will be added to student {{ 'record' | pluralize(targetStudentCount) }}.
                  <span v-if="targetStudentCount >= 500">Are you sure?</span>
                </span>
                <span v-if="!targetStudentCount && (addedCohorts.length || addedCuratedGroups.length)" class="font-italic">
                  <span v-if="addedCohorts.length && !addedCuratedGroups.length">There are no students in the {{ 'cohort' | pluralize(addedCohorts.length, {1: ' '}) }}.</span>
                  <span v-if="addedCuratedGroups.length && !addedCohorts.length">There are no students in the {{ 'group' | pluralize(addedCuratedGroups.length, {1: ' '}) }}.</span>
                  <span v-if="addedCohorts.length && addedCuratedGroups.length">
                    Neither the {{ 'cohort' | pluralize(addedCohorts.length, {1: ' '}) }} nor the {{ 'group' | pluralize(addedCuratedGroups.length, {1: ' '}) }} have students.
                  </span>
                </span>
              </div>
              <div>
                <CreateNoteCohortDropdown
                  v-if="myCohorts && myCohorts.length"
                  :add-object="addCohortToBatch"
                  :clear-errors="clearErrors"
                  :objects="myCohorts"
                  :is-curated-groups-mode="false"
                  :remove-object="removeCohortFromBatch" />
              </div>
              <div>
                <CreateNoteCohortDropdown
                  v-if="myCuratedGroups && myCuratedGroups.length"
                  :add-object="addCuratedGroupToBatch"
                  :clear-errors="clearErrors"
                  :objects="myCuratedGroups"
                  :is-curated-groups-mode="true"
                  :remove-object="removeCuratedGroupFromBatch" />
              </div>
              <hr />
            </div>
            <div>
              <label for="create-note-subject" class="font-size-14 font-weight-bolder mb-1"><span class="sr-only">Note </span>Subject</label>
            </div>
            <div>
              <input
                id="create-note-subject"
                v-model="subject"
                aria-labelledby="create-note-subject-label"
                class="cohort-create-input-name"
                type="text"
                maxlength="255"
                @keydown.esc="cancel()">
            </div>
            <div>
              <label for="create-note-body" class="font-size-14 font-weight-bolder mt-3 mb-1">Note Details</label>
            </div>
            <div id="note-details">
              <span id="create-note-body">
                <ckeditor v-model="body" :editor="editor" :config="editorConfig"></ckeditor>
              </span>
            </div>
          </div>
          <AdvisingNoteTopics
            v-if="undocked"
            class="mt-2 mr-3 mb-1 ml-3"
            :function-add="addTopic"
            :function-remove="removeTopic"
            :topics="topics" />
          <div v-if="undocked" class="mt-2 mr-3 mb-1 ml-3">
            <div v-if="attachmentError" class="mt-3 mb-3 w-100">
              <font-awesome icon="exclamation-triangle" class="text-danger pr-1" />
              <span aria-live="polite" role="alert">{{ attachmentError }}</span>
            </div>
            <div v-if="size(attachments) < maxAttachmentsPerNote" class="w-100">
              <label for="choose-file-for-note-attachment" class="sr-only"><span class="sr-only">Note </span>Attachments</label>
              <div class="choose-attachment-file-wrapper no-wrap pl-3 pr-3 w-100">
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
            <div v-if="size(attachments) === maxAttachmentsPerNote" class="w-100">
              A note can have no more than {{ maxAttachmentsPerNote }} attachments.
            </div>
            <div>
              <ul class="pill-list pl-0 mt-3">
                <li
                  v-for="(attachment, index) in attachments"
                  :id="`new-note-attachment-${index}`"
                  :key="attachment.name"
                  class="mt-2">
                  <span class="pill pill-attachment text-nowrap">
                    <font-awesome icon="paperclip" class="pr-1 pl-1" /> {{ attachment.name }}
                    <b-btn
                      :id="`remove-note-attachment-${index}`"
                      variant="link"
                      class="p-0"
                      @click.prevent="removeAttachment(index)">
                      <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
                      <span class="sr-only">Delete attachment {{ attachment.name }}</span>
                    </b-btn>
                  </span>
                </li>
              </ul>
            </div>
          </div>
          <hr />
          <div class="d-flex mt-1 mr-3 mb-0 ml-3">
            <div class="flex-grow-1">
              <b-btn
                v-if="!undocked"
                id="btn-to-advanced-note-options"
                variant="link"
                @click.prevent="setNewNoteMode('advanced')">
                Advanced note options
              </b-btn>
            </div>
            <div>
              <b-btn
                id="create-note-button"
                class="btn-primary-color-override"
                :disabled="!targetStudentCount || !subject"
                aria-label="Create new note"
                variant="primary"
                @click.prevent="create()">
                Save
              </b-btn>
            </div>
            <div>
              <b-btn
                id="create-note-cancel"
                variant="link"
                :class="{'sr-only': !undocked}"
                @click.prevent="cancel()">
                Cancel
              </b-btn>
            </div>
          </div>
        </form>
      </div>
    </FocusLock>
    <div v-if="!isMinimizing && newNoteMode === 'minimized'" class="minimized-placeholder d-flex align-items-end ml-3 mr-3">
      <div class="flex-grow-1 new-note-header">
        New Note
      </div>
      <div class="pr-0">
        <b-btn
          id="maximize-new-note-modal"
          aria-label="Bring create-note form into view"
          variant="link"
          class="pr-2"
          @click.stop="maximize()">
          <span class="sr-only">Maximize</span>
          <font-awesome icon="window-maximize" class="fa-icon-size text-white" />
        </b-btn>
      </div>
      <div class="pr-2 pt-1">
        <b-btn
          id="cancel-minimized-new-note"
          aria-label="Cancel the create-note form"
          variant="link"
          class="pl-1"
          @click.prevent="cancel()">
          <span class="sr-only">Cancel</span>
          <font-awesome icon="times" class="fa-icon-size text-white" />
        </b-btn>
      </div>
    </div>
    <AreYouSureModal
      v-if="showDiscardModal"
      :function-cancel="cancelTheDiscard"
      :function-confirm="discardConfirmed"
      modal-header="Discard unsaved note?"
      :show-modal="showDiscardModal" />
    <b-popover
      v-if="showErrorPopover"
      :show.sync="showErrorPopover"
      placement="top"
      target="create-note-subject"
      title="">
      <span class="has-error">{{ error }}</span>
    </b-popover>
  </div>
</template>

<script>
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics';
import AreYouSureModal from '@/components/util/AreYouSureModal';
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';
import Context from '@/mixins/Context';
import CreateNoteCohortDropdown from '@/components/note/CreateNoteCohortDropdown';
import FocusLock from 'vue-focus-lock';
import NoteUtil from '@/components/note/NoteUtil';
import StudentEditSession from '@/mixins/StudentEditSession';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { createNote } from '@/api/notes';

require('@/assets/styles/ckeditor-custom.css');

export default {
  name: 'NewNoteModal',
  components: {AdvisingNoteTopics, AreYouSureModal, CreateNoteCohortDropdown, FocusLock},
  mixins: [Context, NoteUtil, StudentEditSession, UserMetadata, Util],
  props: {
    disable: Boolean,
    initialMode: {
      default: 'docked',
      required: false,
      type: String
    },
    onSubmit: {
      required: true,
      type: Function
    },
    onSuccessfulCreate: {
      required: true,
      type: Function
    },
    sid: {
      required: false,
      type: String
    }
  },
  data: () => ({
    addedCohorts: [],
    addedCuratedGroups: [],
    attachment: undefined,
    attachmentError: undefined,
    attachments: [],
    body: undefined,
    editor: ClassicEditor,
    editorConfig: {
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link'],
    },
    error: undefined,
    isMinimizing: false,
    showErrorPopover: false,
    showDiscardModal: false,
    sids: undefined,
    subject: undefined,
    targetStudentCount: undefined,
    topics: []
  }),
  computed: {
    undocked() {
      return this.includes(['advanced', 'batch'], this.newNoteMode);
    }
  },
  watch: {
    attachment() {
      if (this.validateAttachment()) {
        this.attachments.push(this.attachment);
        this.alertScreenReader(`Attachment '${name}' added`);
      }
      this.$refs['attachment-file-input'].reset();
    },
    body(b) {
      if (b) this.clearErrors();
    },
    subject(s) {
      if (s) this.clearErrors();
    }
  },
  created() {
    this.initFileDropPrevention();
    this.sids = this.sid ? [ this.sid ] : [];
    this.reset();
  },
  methods: {
    addTopic(topic) {
      this.topics.push(topic);
    },
    cancel() {
      this.clearErrors();
      const unsavedChanges = this.trim(this.subject) || this.stripHtmlAndTrim(this.body) || this.size(this.attachments) || this.addedCohorts.length || this.addedCuratedGroups.length;
      if (unsavedChanges) {
        this.showDiscardModal = true;
      } else {
        this.discardConfirmed();
      }
    },
    discardConfirmed() {
      this.showDiscardModal = false;
      this.reset();
      this.alertScreenReader("Cancelled create new note");
    },
    cancelTheDiscard() {
      this.showDiscardModal = false;
      this.putFocusNextTick('create-note-subject');
    },
    clearErrors() {
      this.attachmentError = null;
      this.error = null;
      this.showErrorPopover = false;
    },
    create() {
      const isBatchMode = this.newNoteMode === 'batch';
      this.subject = this.trim(this.subject);
      if (this.subject && this.targetStudentCount) {
        this.body = this.trim(this.body);
        this.setNewNoteMode('saving');
        this.onSubmit();
        const addedCohortIds = this.map(this.addedCohorts, 'id');
        const addedCuratedGroupIds = this.map(this.addedCuratedGroups, 'id');
        createNote(
          isBatchMode,
          this.sids,
          this.subject,
          this.body,
          this.topics,
          this.attachments,
          addedCohortIds,
          addedCuratedGroupIds
        ).then(data => {
          this.reset();
          this.onSuccessfulCreate(data);
          this.alertScreenReader("New note saved.");
        });
      } else {
        this.error = 'Subject is required';
        this.showErrorPopover = true;
        this.alertScreenReader(`Validation failed: ${this.error}`);
        this.putFocusNextTick('create-note-subject');
      }
    },
    maximize() {
      this.setNewNoteMode('docked');
      this.alertScreenReader("Create note form is visible.");
      this.putFocusNextTick('create-note-subject');
    },
    minimize() {
      this.isMinimizing = true;
      this.setNewNoteMode('minimized');
      setTimeout(() => this.isMinimizing = false, 300);
      this.alertScreenReader("Create note form minimized.");
    },
    openNewNoteModal() {
       this.setNewNoteMode(this.initialMode);
       this.putFocusNextTick('create-note-subject');
    },
    addCohortToBatch(cohort) {
      this.targetStudentCount += cohort.totalStudentCount;
      this.addedCohorts.push(cohort);
    },
    removeCohortFromBatch(cohort) {
      this.targetStudentCount -= cohort.totalStudentCount;
      this.addedCohorts = this.filterList(this.addedCohorts, c => c.id !== cohort.id);
    },
    addCuratedGroupToBatch(curatedGroup) {
      this.targetStudentCount += curatedGroup.studentCount;
      this.addedCuratedGroups.push(curatedGroup);
    },
    removeCuratedGroupFromBatch(curatedGroup) {
      this.targetStudentCount -= curatedGroup.studentCount;
      this.addedCuratedGroups = this.filterList(this.addedCuratedGroups, c => c.id !== curatedGroup.id);
    },
    removeAttachment(index) {
      this.clearErrors();
      this.alertScreenReader(`Attachment '${this.attachments[index].name}' removed`);
      this.attachments.splice(index, 1);
    },
    removeTopic(topic) {
      let index = this.topics.indexOf(topic);
      this.topics.splice(index, 1);
    },
    reset(mode) {
      this.clearErrors();
      this.setNewNoteMode(mode);
      this.subject = this.body = undefined;
      this.addedCohorts = [];
      this.addedCuratedGroups = [];
      this.attachments = [];
      this.topics = [];
      this.targetStudentCount = this.sids.length;
    }
  }
}
</script>

<style scoped>
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
.fa-icon-size {
  font-size: 28px;
}
.form-control-file {
  height: 100%;
}
.minimize-icon {
  font-size: 24px;
}
.minimized-placeholder {
  background-color: #125074;
  border: 1px solid #aaa;
  bottom: 0;
  box-shadow: 0 0 10px #ccc;
  color: #fff;
  height: 50px;
  position: fixed;
  right: 10px;
  width: 30%;
  z-index: 2;
}
.modal-full-screen {
  display: block;
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgb(0,0,0);
  background-color: rgba(0,0,0,0.4);
}
.modal-full-screen-content {
  background-color: #fff;
  margin: 140px auto auto auto;
  padding-bottom: 20px;
  border: 1px solid #888;
  width: 60%;
}
.modal-minimized {
  height: 1px !important;
  z-index: 1;
}
.modal-open {
  -webkit-transition: height 0.5s;
  background-color: #fff;
  border: 1px solid #aaa;
  bottom: 0;
  box-shadow: 0 0 10px #ccc;
  height: 480px;
  position: fixed;
  right: 30px;
  transition: height 0.5s;
  width: 30%;
  z-index: 1;
}
.modal-saving {
  height: 1px !important;
}
.new-note-header {
  font-size: 24px;
  margin: 0 15px 12px 15px;
}
</style>
