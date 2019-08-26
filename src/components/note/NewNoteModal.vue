<template>
  <div>
    <div :class="{'d-flex justify-content-center pl-3 pr-3': showBatchNoteFeatures}">
      <b-btn
        :id="showBatchNoteFeatures ? 'batch-note-button' : 'new-note-button'"
        class="mt-1 mr-2 btn-primary-color-override btn-primary-color-override-opaque"
        :class="{'w-100': showBatchNoteFeatures}"
        variant="primary"
        :disabled="isModalOpen"
        @click="openNewNoteModal()">
        <span class="m-1">
          <font-awesome icon="file-alt" />
          <span class="sr-only">{{ showBatchNoteFeatures ? 'Batch create ' : 'Create ' }}</span>
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
          'd-none': isNil(noteMode),
          'modal-open': noteMode === 'docked',
          'modal-open modal-minimized': noteMode === 'minimized',
          'modal-open modal-saving': noteMode === 'saving',
          'modal-full-screen-content': undocked,
          'mt-4': showBatchNoteFeatures
        }">
        <form @submit.prevent="createNote()">
          <NewNotePageHeader
            :cancel="cancel"
            :delete-template="deleteTemplate"
            :edit-template="editTemplate"
            :load-template="loadTemplate"
            :minimize="minimize" />
          <hr class="m-0" />
          <div class="mt-2 mr-3 mb-1 ml-3">
            <div v-if="showBatchNoteFeatures" :class="{'batch-mode-features': noteMode === 'batch'}">
              <NewBatchNoteFeatures :cancel="cancel" />
              <hr />
            </div>
            <div>
              <label for="create-note-subject" class="font-size-14 font-weight-bolder mb-1"><span class="sr-only">Note </span>Subject</label>
            </div>
            <div>
              <input
                id="create-note-subject"
                v-model="noteSubject"
                aria-labelledby="create-note-subject-label"
                class="cohort-create-input-name"
                maxlength="255"
                type="text"
                @keydown.esc="cancel()">
            </div>
            <div>
              <label for="create-note-body" class="font-size-14 font-weight-bolder mt-3 mb-1">Note Details</label>
            </div>
            <div id="note-details">
              <span id="create-note-body">
                <ckeditor v-model="noteBody" :editor="editor" :config="editorConfig"></ckeditor>
              </span>
            </div>
          </div>
          <div v-if="undocked">
            <div v-if="suggestedTopics">
              <AdvisingNoteTopics
                class="mt-2 mr-3 mb-1 ml-3"
                :function-add="addTopic"
                :function-remove="removeTopic"
                :suggested-topics="suggestedTopics"
                :topics="topics" />
            </div>
            <AdvisingNoteAttachments
              class="mt-2 mr-3 mb-1 ml-3"
              :add-attachment="addAttachment"
              :existing-attachments="attachments"
              :remove-attachment="removeAttachment" />
          </div>
          <hr />
          <div>
            <NewNoteModalButtons
              :cancel="cancel"
              :create-note="createNote"
              :delete-template="deleteTemplate"
              :minimize="minimize"
              :save-as-template="saveAsTemplate"
              :update-template="updateTemplate" />
          </div>
        </form>
      </div>
    </FocusLock>
    <NewNoteMinimized v-if="!isMinimizing && noteMode === 'minimized'" :cancel="cancel" />
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
    deleteTemplateId: undefined,
    editor: ClassicEditor,
    editorConfig: {
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link'],
    },
    isMinimizing: false,
    isModalOpen: false,
    noteBody: undefined,
    noteSubject: undefined,
    showBatchNoteFeatures: undefined,
    showCreateTemplateModal: false,
    showDiscardNoteModal: false,
    showDiscardTemplateModal: false,
    showErrorPopover: false,
    template: undefined
  }),
  watch: {
    // Vuex-managed 'body' and 'subject' cannot be bound to ckeditor v-model. Thus, we have the following aliases.
    noteBody(value) {
      this.setBody(value);
    },
    noteSubject(value) {
      this.setSubject(value);
    }
  },
  mounted() {
    this.showBatchNoteFeatures = !this.student;
  },
  methods: {
    cancel() {
      if (this.noteMode === 'editTemplate') {
        if (this.templateEquals(this, this.template)) {
          this.discardTemplate();
        } else {
          this.showDiscardTemplateModal = true;
        }
      } else {
        const unsavedChanges = this.trim(this.subject) || this.stripHtmlAndTrim(this.body) || this.size(this.attachments) || this.addedCohorts.length || this.addedCuratedGroups.length;
        if (unsavedChanges) {
          this.showDiscardNoteModal = true;
        } else {
          this.discardNote();
        }
      }
    },
    editTemplate(template) {
      this.init({
        note: template,
        sids: this.sids,
        noteMode: 'editTemplate'
      });
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
    },
    cancelDiscardTemplate() {
      this.template = undefined;
      this.showDiscardTemplateModal = false;
      this.isModalOpen = false;
    },
    createNote() {
      if (this.subject && this.targetStudentCount) {
        this.onSubmit();
        this.createAdvisingNote(this.showBatchNoteFeatures).then(() => {
          this.onSuccessfulCreate();
          this.reset();
          this.setNoteMode(null);
          this.isModalOpen = false;
          this.alertScreenReader(this.showBatchNoteFeatures ? `Note created for ${this.targetStudentCount} students.` : "New note saved.");
        });
      }
    },
    createTemplate(title) {
      this.showCreateTemplateModal = false;
      createNoteTemplate(title, this.subject, this.body || '', this.topics, this.attachments).then(template => {
        this.alertScreenReader(`Template ${template.label} created`);
      });
    },
    deleteTemplate(templateId) {
      this.deleteTemplateId = templateId;
    },
    deleteTemplateConfirmed() {
      deleteNoteTemplate(this.deleteTemplateId).then(() => {
        this.deleteTemplateId = null;
      })
    },
    discardNote() {
      this.showDiscardNoteModal = false;
      this.reset();
      this.setNoteMode(null);
      this.isModalOpen = false;
      this.alertScreenReader("Cancelled create new note");
    },
    discardTemplate() {
      this.showDiscardTemplateModal = false;
      this.reset(this.showBatchNoteFeatures ? 'batch' : 'advanced');
      this.alertScreenReader("Cancelled create new template");
    },
    getTemplateTitle(templateId) {
      const template = this.find(this.noteTemplates, ['id', templateId]);
      return this.get(template, 'title');
    },
    loadTemplate(template) {
      this.noteSubject = template.subject;
      this.noteBody = template.body;
      this.init({
        note: template,
        noteMode: this.noteMode
      });
      this.alertScreenReader(`Template ${template.title} loaded`);
    },
    minimize() {
      this.isMinimizing = true;
      this.setNoteMode('minimized');
      setTimeout(() => this.isMinimizing = false, 300);
      this.alertScreenReader("Create note form minimized.");
    },
    openNewNoteModal() {
      this.init({
        noteMode: this.showBatchNoteFeatures ? 'batch' : 'docked'
      });
      if (this.student) {
        this.addSid(this.student.sid);
      }
      this.isModalOpen = true;
      this.putFocusNextTick(this.showBatchNoteFeatures ? 'create-note-add-student-input' : 'create-note-subject');
      this.alertScreenReader(this.showBatchNoteFeatures ? 'Create batch note form is open.' : 'Create note form is open');
    },
    reset() {
      this.resetSession();
      this.noteSubject = null;
      this.noteBody = null;
    },
    saveAsTemplate() {
      this.showCreateTemplateModal = true;
    },
    updateTemplate() {
      updateNoteTemplate(this.template.id, this.subject, this.body || '', this.topics, this.attachments, []);
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
.batch-mode-features {
  -webkit-transition: height 0.5s;
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
</style>
