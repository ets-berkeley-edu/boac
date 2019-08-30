<template>
  <div>
    <div :class="{'d-flex justify-content-center pl-3 pr-3': isBatchFeature}">
      <b-btn
        :id="isBatchFeature ? 'batch-note-button' : 'new-note-button'"
        class="mt-1 mr-2 btn-primary-color-override btn-primary-color-override-opaque"
        :class="{'w-100': isBatchFeature}"
        variant="primary"
        :disabled="isModalOpen"
        @click="openNewNoteModal()">
        <span class="m-1">
          <font-awesome icon="file-alt" />
          <span class="sr-only">{{ isBatchFeature ? 'Batch create ' : 'Create ' }}</span>
          New Note
        </span>
      </b-btn>
    </div>
    <FocusLock
      v-if="isModalOpen"
      :disabled="!undocked || showDiscardNoteModal || showCreateTemplateModal || !!deleteTemplateId || showDiscardTemplateModal"
      :class="{'modal-full-screen': undocked}">
      <div
        id="new-note-modal-container"
        :class="{
          'd-none': isNil(mode),
          'modal-open': mode === 'docked',
          'modal-open modal-minimized': mode === 'minimized',
          'modal-open modal-saving': mode === 'saving',
          'modal-full-screen-content': undocked,
          'mt-4': isBatchFeature
        }">
        <form @submit.prevent="createNote()">
          <NewNotePageHeader
            :cancel="cancelRequested"
            :delete-template="deleteTemplate"
            :edit-template="editTemplate"
            :load-template="loadTemplate"
            :minimize="minimize"
            :undocked="undocked" />
          <div class="ml-2 mr-3 pl-2 pr-2">
            <b-alert
              id="alert"
              class="font-weight-bolder w-100"
              :show="dismissAlertSeconds"
              dismissible
              fade
              variant="info"
              @dismiss-count-down="dismissAlert">
              {{ alert }}
            </b-alert>
          </div>
          <hr class="m-0" />
          <div class="mt-2 mr-3 mb-1 ml-3">
            <transition v-if="isBatchFeature" name="batch">
              <div v-if="!includes(['createTemplate', 'editTemplate'], mode)">
                <NewBatchNoteFeatures :cancel="cancelRequested" />
                <hr />
              </div>
            </transition>
            <div>
              <label for="create-note-subject" class="font-size-14 font-weight-bolder mb-1"><span class="sr-only">Note </span>Subject</label>
            </div>
            <div>
              <input
                id="create-note-subject"
                :value="model.subject"
                aria-labelledby="create-note-subject-label"
                class="cohort-create-input-name"
                maxlength="255"
                type="text"
                @input="setSubjectPerEvent"
                @keydown.esc="cancelRequested()">
            </div>
            <div>
              <label for="create-note-body" class="font-size-14 font-weight-bolder mt-3 mb-1">Note Details</label>
            </div>
            <div id="note-details">
              <span id="create-note-body">
                <ckeditor
                  :value="model.body || ''"
                  :editor="editor"
                  :config="editorConfig"
                  @input="setBodyPerEvent"></ckeditor>
              </span>
            </div>
          </div>
          <div v-if="undocked">
            <AdvisingNoteTopics
              :key="model.id"
              class="mt-2 mr-3 mb-1 ml-3"
              :function-add="addTopic"
              :function-remove="removeTopic"
              :topics="model.topics" />
            <AdvisingNoteAttachments
              class="mt-2 mr-3 mb-1 ml-3"
              :add-attachment="addAttachment"
              :existing-attachments="model.attachments"
              :remove-attachment="removeAttachment" />
          </div>
          <hr />
          <div>
            <NewNoteModalButtons
              :cancel="cancelRequested"
              :create-note="createNote"
              :create-template="saveAsTemplate"
              :delete-template="deleteTemplate"
              :minimize="minimize"
              :update-template="updateTemplate"
              :undocked="undocked" />
          </div>
        </form>
      </div>
    </FocusLock>
    <div v-if="!isMinimizing && mode === 'minimized'">
      <NewNoteMinimized :cancel="cancelRequested" />
    </div>
    <AreYouSureModal
      v-if="showDiscardNoteModal"
      :function-cancel="cancelDiscardNote"
      :function-confirm="discardNote"
      modal-header="Discard unsaved note?"
      :show-modal="showDiscardNoteModal" />
    <CreateTemplateModal
      v-if="showCreateTemplateModal"
      button-label-confirm="Save"
      :cancel="cancelCreateTemplate"
      :create="createTemplate"
      modal-header="Name Your Template"
      :show-modal="showCreateTemplateModal" />
    <AreYouSureModal
      v-if="!!deleteTemplateId"
      button-label-confirm="Delete"
      :function-cancel="cancelDeleteTemplate"
      :function-confirm="deleteTemplateConfirmed"
      :modal-body="`Are you sure you want to delete the <b>'${getTemplateTitle(deleteTemplateId)}'</b> template?`"
      modal-header="Delete Template"
      :show-modal="!!deleteTemplateId" />
    <AreYouSureModal
      v-if="showDiscardTemplateModal"
      :function-cancel="cancelDiscardTemplate"
      :function-confirm="discardTemplate"
      modal-header="Discard unsaved template?"
      :show-modal="showDiscardTemplateModal" />
  </div>
</template>

<script>
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments';
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics';
import AreYouSureModal from '@/components/util/AreYouSureModal';
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';
import Context from '@/mixins/Context';
import CreateTemplateModal from "@/components/note/CreateTemplateModal";
import FocusLock from 'vue-focus-lock';
import NewBatchNoteFeatures from '@/components/note/NewBatchNoteFeatures';
import NoteEditSession from '@/mixins/NoteEditSession';
import NewNoteMinimized from '@/components/note/NewNoteMinimized';
import NewNoteModalButtons from '@/components/note/NewNoteModalButtons';
import NewNotePageHeader from '@/components/note/NewNotePageHeader';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { createNoteTemplate, deleteNoteTemplate, updateNoteTemplate } from '@/api/note-templates';

require('@/assets/styles/ckeditor-custom.css');

export default {
  name: 'NewNoteModal',
  components: {
    AdvisingNoteAttachments,
    AdvisingNoteTopics,
    AreYouSureModal,
    CreateTemplateModal,
    NewBatchNoteFeatures,
    NewNoteMinimized,
    NewNoteModalButtons,
    NewNotePageHeader,
    FocusLock
  },
  mixins: [Context, NoteEditSession, UserMetadata, Util],
  props: {
    onSubmit: {
      required: false,
      default: () => {},
      type: Function
    },
    onSuccessfulCreate: {
      required: false,
      default: () => {},
      type: Function
    },
    student: {
      required: false,
      type: Object
    }
  },
  data: () => ({
    alert: undefined,
    deleteTemplateId: undefined,
    dismissAlertSeconds: 0,
    editor: ClassicEditor,
    editorConfig: {
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link'],
    },
    isMinimizing: false,
    isModalOpen: false,
    isBatchFeature: undefined,
    showCreateTemplateModal: false,
    showDiscardNoteModal: false,
    showDiscardTemplateModal: false,
    showErrorPopover: false
  }),
  computed: {
    undocked() {
      return this.includes(['advanced', 'batch', 'createTemplate', 'editTemplate'], this.mode);
    }
  },
  mounted() {
    this.isBatchFeature = !this.student;
  },
  methods: {
    cancelRequested() {
      if (this.mode === 'createTemplate') {
        const unsavedChanges = this.trim(this.model.subject)
          || this.stripHtmlAndTrim(this.model.body)
          || this.size(this.model.topics)
          || this.size(this.model.attachments);
        if (unsavedChanges) {
          this.showDiscardTemplateModal = true;
        } else {
          this.discardTemplate();
        }
      } else if (this.mode === 'editTemplate') {
        const indexOf = this.noteTemplates.findIndex(t => t.id === this.model.id);
        const template = this.noteTemplates[indexOf];
        const noDiff = this.trim(this.model.subject) === template.subject
          && this.model.body === template.body
          && !this.size(this.xor(this.model.topics, template.topics))
          && !this.size(this.xorBy(this.model.attachments, template.attachments, 'displayName'));
        if (noDiff) {
          this.discardTemplate();
        } else {
          this.showDiscardTemplateModal = true;
        }
      } else {
        const unsavedChanges = this.trim(this.model.subject)
          || this.stripHtmlAndTrim(this.model.body)
          || this.size(this.model.topics)
          || this.size(this.model.attachments)
          || this.addedCohorts.length
          || this.addedCuratedGroups.length;
        if (unsavedChanges) {
          this.showDiscardNoteModal = true;
        } else {
          this.discardNote();
        }
      }
    },
    cancelCreateTemplate() {
      this.showCreateTemplateModal = false;
    },
    cancelDiscardNote() {
      this.showDiscardNoteModal = false;
      this.putFocusNextTick('create-note-subject');
      this.alertScreenReader(`Continue editing note.`);
    },
    cancelDeleteTemplate() {
      this.deleteTemplateId = null;
      this.putFocusNextTick('create-note-subject');
    },
    cancelDiscardTemplate() {
      this.showDiscardTemplateModal = false;
      this.putFocusNextTick('create-note-subject');
    },
    createNote() {
      if (this.model.subject && this.targetStudentCount) {
        this.onSubmit();
        this.createAdvisingNote(this.isBatchFeature).then(() => {
          this.isModalOpen = false;
          this.onSuccessfulCreate();
          this.terminate();
          this.alertScreenReader(this.isBatchFeature ? `Note created for ${this.targetStudentCount} students.` : "New note saved.");
        });
      }
    },
    createTemplate(title) {
      this.showCreateTemplateModal = false;
      createNoteTemplate(title, this.model.subject, this.model.body || '', this.model.topics, this.model.attachments).then(() => {
        this.onSuccessfulCreate();
        this.beginEditSession({
          mode: this.isBatchFeature ? 'batch' : 'advanced',
          model: null,
          sid: this.get(this.student, 'sid')
        });
        const alert = `New template '${title}' created.`;
        this.showAlert(alert);
        this.alertScreenReader(alert);
      });
    },
    deleteTemplate(templateId) {
      this.deleteTemplateId = templateId;
    },
    deleteTemplateConfirmed() {
      deleteNoteTemplate(this.deleteTemplateId).then(() => {
        this.deleteTemplateId = null;
        this.putFocusNextTick('create-note-subject');
      })
    },
    discardNote() {
      this.showDiscardNoteModal = false;
      this.isModalOpen = false;
      this.terminate();
      this.alertScreenReader('Cancelled create new note');
    },
    discardTemplate() {
      this.showDiscardTemplateModal = false;
      this.beginEditSession({
        mode: this.isBatchFeature ? 'batch' : 'advanced',
        model: null,
        sid: this.get(this.student, 'sid')
      });
      this.putFocusNextTick('create-note-subject');
      const alert = 'Cancelled the create template form.';
      this.showAlert(alert);
      this.alertScreenReader(alert);
    },
    dismissAlert(seconds) {
      this.dismissAlertSeconds = seconds;
      if (seconds === 0) {
        this.alert = undefined;
      }
    },
    editTemplate(template) {
      this.beginEditSession({
        mode: 'editTemplate',
        model: this.cloneDeep(template),
        sid: this.get(this.student, 'sid')
      });
      this.putFocusNextTick('create-note-subject');
    },
    getTemplateTitle(templateId) {
      const template = this.find(this.noteTemplates, ['id', templateId]);
      return this.get(template, 'title');
    },
    loadTemplate(template) {
      this.beginEditSession({
        mode: this.mode,
        model: this.cloneDeep(template),
        sid: this.get(this.student, 'sid')
      });
      this.putFocusNextTick('create-note-subject');
      this.alertScreenReader(`Template ${template.title} loaded`);
    },
    minimize() {
      this.isMinimizing = true;
      this.setMode('minimized');
      setTimeout(() => this.isMinimizing = false, 300);
      this.alertScreenReader('Create note form minimized.');
    },
    openNewNoteModal() {
      this.beginEditSession({
        mode: this.isBatchFeature ? 'batch' : 'docked',
        model: undefined,
        sid: this.get(this.student, 'sid')
      });
      this.isModalOpen = true;
      this.putFocusNextTick(this.isBatchFeature ? 'create-note-add-student-input' : 'create-note-subject');
      this.alertScreenReader(this.isBatchFeature ? 'Create batch note form is open.' : 'Create note form is open');
    },
    saveAsTemplate() {
      this.showCreateTemplateModal = true;
      this.putFocusNextTick('template-title-input');
    },
    showAlert(alert) {
      this.alert = alert;
      this.dismissAlertSeconds = 5;
    },
    updateTemplate() {
      const newAttachments = this.filterList(this.model.attachments, a => !a.id);
      updateNoteTemplate(
        this.model.id,
        this.model.subject,
        this.model.body,
        this.model.topics,
        newAttachments,
        this.model.deleteAttachmentIds
      ).then(template => {
        this.terminate();
        this.isModalOpen = false;
        this.alertScreenReader(`Template ${template.label} updated`);
      });
    }
  }
}
</script>

<style scoped>
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
  min-height: 480px;
  position: fixed;
  right: 30px;
  transition: height 0.5s;
  width: 30%;
  z-index: 1;
}
.modal-saving {
  height: 1px !important;
}
.batch-enter-active {
   -webkit-transition-duration: 0.3s;
   transition-duration: 0.3s;
   -webkit-transition-timing-function: ease-in;
   transition-timing-function: ease-in;
}
.batch-leave-active {
   -webkit-transition-duration: 0.3s;
   transition-duration: 0.5s;
   -webkit-transition-timing-function: cubic-bezier(0, 1, 0.5, 1);
   transition-timing-function: cubic-bezier(0, 1, 0.5, 1);
}
.batch-enter-to, .batch-leave {
  max-height: 280px;
  overflow: hidden;
}
.batch-enter, .batch-leave-to {
  overflow: hidden;
  max-height: 0;
}
</style>
