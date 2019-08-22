<template>
  <div>
    <div :class="{'d-flex justify-content-center pl-3 pr-3': initialMode === 'batch'}">
      <b-btn
        :id="initialMode === 'batch' ? 'batch-note-button' : 'new-note-button'"
        class="mt-1 mr-2 btn-primary-color-override btn-primary-color-override-opaque"
        :class="{'w-100': initialMode === 'batch'}"
        variant="primary"
        :disabled="disable || !!noteMode"
        @click="openNewNoteModal()">
        <span class="m-1">
          <font-awesome icon="file-alt" />
          <span class="sr-only">{{ initialMode === 'batch' ? 'Batch create ' : 'Create ' }}</span>
          New Note
        </span>
      </b-btn>
    </div>
    <FocusLock
      v-if="!disable"
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
          'mt-4': initialMode === 'batch'
        }">
        <form @submit.prevent="createNote()">
          <div class="d-flex align-items-end pt-2 mb-1" :class="{'mt-2': undocked}">
            <div class="flex-grow-1 new-note-header font-weight-bolder">
              <span v-if="noteMode === 'editTemplate'">Edit Template</span>
              <span v-if="noteMode !== 'editTemplate'">New Note</span>
            </div>
            <div v-if="undocked" class="mr-4">
              <b-dropdown
                v-if="noteMode !== 'editTemplate'"
                id="my-templates-button"
                text="Templates"
                aria-label="Select a note template"
                variant="primary"
                class="mb-2 ml-0"
                right>
                <b-dropdown-header v-if="!size(noteTemplates)" id="no-templates-header">
                  <div class="font-weight-bolder">Templates</div>
                  <div>
                    <div class="font-weight-bolder">You have no saved templates.</div>
                    <div>To begin, create a new note and select, "Save note as template," to build your first note template.</div>
                  </div>
                </b-dropdown-header>
                <b-dropdown-item
                  v-for="template in noteTemplates"
                  :id="`note-template-${template.id}`"
                  :key="template.id">
                  <div class="align-items-center d-flex justify-content-between">
                    <div>
                      <b-btn variant="link" class="dropdown-item p-0" @click="loadTemplate(template)">{{ truncate(template.title) }}</b-btn>
                    </div>
                    <div class="align-items-center d-flex ml-2 no-wrap">
                      <div>
                        <b-btn variant="link" class="p-0" @click="editNoteTemplate(template)">Edit</b-btn>
                      </div>
                      <div>
                        |
                      </div>
                      <div>
                        <b-btn variant="link" class="p-0" @click="deleteNoteTemplate(template.id)">Delete</b-btn>
                      </div>
                    </div>
                  </div>
                </b-dropdown-item>
              </b-dropdown>
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
            <div v-if="initialMode === 'batch'" :class="{'batch-mode-features': noteMode === 'batch'}">
              <div>
                <span aria-live="polite" role="alert">
                  <span
                    v-if="targetStudentCount"
                    id="target-student-count-alert"
                    class="font-italic"
                    :class="{'has-error': targetStudentCount >= 250, 'font-weight-bolder': targetStudentCount >= 500}">
                    Note will be added to {{ 'student record' | pluralize(targetStudentCount) }}.
                    <span v-if="targetStudentCount >= 500">Are you sure?</span>
                  </span>
                  <span v-if="!targetStudentCount && (addedCohorts.length || addedCuratedGroups.length)" class="font-italic">
                    <span
                      v-if="addedCohorts.length && !addedCuratedGroups.length"
                      id="no-students-per-cohorts-alert">There are no students in the {{ 'cohort' | pluralize(addedCohorts.length, {1: ' '}) }}.</span>
                    <span
                      v-if="addedCuratedGroups.length && !addedCohorts.length"
                      id="no-students-per-curated-groups-alert">There are no students in the {{ 'group' | pluralize(addedCuratedGroups.length, {1: ' '}) }}.</span>
                    <span
                      v-if="addedCohorts.length && addedCuratedGroups.length"
                      id="no-students-alert">
                      Neither the {{ 'cohort' | pluralize(addedCohorts.length, {1: ' '}) }} nor the {{ 'group' | pluralize(addedCuratedGroups.length, {1: ' '}) }} have students.
                    </span>
                  </span>
                </span>
              </div>
              <div>
                <CreateNoteAddStudent
                  :add-sid="addSid"
                  dropdown-class="position-relative"
                  :on-esc-form-input="cancel"
                  :remove-sid="removeSid">
                </CreateNoteAddStudent>
              </div>
              <div>
                <CreateNoteCohortDropdown
                  v-if="myCohorts && myCohorts.length"
                  :add-object="addCohortToBatch"
                  :objects="myCohorts"
                  :is-curated-groups-mode="false"
                  :remove-object="removeCohortFromBatch" />
              </div>
              <div>
                <CreateNoteCohortDropdown
                  v-if="myCuratedGroups && myCuratedGroups.length"
                  :add-object="addCuratedGroupToBatch"
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
          <AdvisingNoteAttachments
            v-if="undocked"
            class="mt-2 mr-3 mb-1 ml-3"
            :add-attachment="addAttachment"
            :existing-attachments="attachments" />
          <hr />
          <div class="d-flex mt-1 mr-3 mb-0 ml-3">
            <div v-if="undocked && noteMode !== 'editTemplate'" class="flex-grow-1">
              <b-btn
                id="btn-to-save-note-as-template"
                variant="link"
                :disabled="!trim(subject)"
                @click.prevent="saveAsTemplate()">
                Save note as template
              </b-btn>
            </div>
            <div class="flex-grow-1">
              <b-btn
                v-if="!undocked"
                id="btn-to-advanced-note-options"
                variant="link"
                @click.prevent="setNoteMode('advanced')">
                Advanced note options
              </b-btn>
            </div>
            <div v-if="noteMode === 'editTemplate'">
              <b-btn
                id="update-template-button"
                class="btn-primary-color-override"
                :disabled="!subject"
                aria-label="Update note template"
                variant="primary"
                @click.prevent="updateTemplate()">
                Update Template
              </b-btn>
            </div>
            <div v-if="noteMode !== 'editTemplate'">
              <b-btn
                id="create-note-button"
                class="btn-primary-color-override"
                :disabled="!targetStudentCount || !trim(subject)"
                aria-label="Create new note"
                variant="primary"
                @click.prevent="createNote()">
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
    <div v-if="!isMinimizing && noteMode === 'minimized'" class="minimized-placeholder d-flex align-items-end ml-3 mr-3">
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
      :function-confirm="deleteTemplate"
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
import CreateNoteAddStudent from '@/components/note/CreateNoteAddStudent';
import CreateNoteCohortDropdown from '@/components/note/CreateNoteCohortDropdown';
import CreateTemplateModal from "@/components/note/CreateTemplateModal";
import FocusLock from 'vue-focus-lock';
import Notes from '@/mixins/Notes';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { createNote, createNoteBatch, getDistinctStudentCount } from '@/api/notes';
import { createNoteTemplate, deleteNoteTemplate, updateNoteTemplate } from '@/api/note-templates';

require('@/assets/styles/ckeditor-custom.css');

export default {
  name: 'NewNoteModal',
  components: {
    AdvisingNoteAttachments,
    AdvisingNoteTopics,
    AreYouSureModal,
    CreateNoteAddStudent,
    CreateNoteCohortDropdown,
    CreateTemplateModal,
    FocusLock
  },
  mixins: [Context, Notes, UserMetadata, Util],
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
    attachments: [],
    body: undefined,
    deleteTemplateId: undefined,
    editor: ClassicEditor,
    editorConfig: {
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link'],
    },
    isMinimizing: false,
    showCreateTemplateModal: false,
    showDiscardNoteModal: false,
    showDiscardTemplateModal: false,
    showErrorPopover: false,
    sids: undefined,
    subject: undefined,
    targetStudentCount: undefined,
    topics: []
  }),
  computed: {
    undocked() {
      return this.includes(['advanced', 'batch', 'editTemplate'], this.noteMode);
    }
  },
  created() {
    this.reset();
    this.sids = this.sid ? [ this.sid ] : [];
    this.targetStudentCount = this.sids.length;
  },
  methods: {
    addAttachment(attachment) {
      this.attachments.push(attachment);
    },
    addCohortToBatch(cohort) {
      this.addedCohorts.push(cohort);
      this.alertScreenReader(`Added cohort '${cohort.name}'`);
      this.recalculateStudentCount();
    },
    addCuratedGroupToBatch(curatedGroup) {
      this.addedCuratedGroups.push(curatedGroup);
      this.alertScreenReader(`Added curated group '${curatedGroup.name}'`);
      this.recalculateStudentCount();
    },
    addSid(sid) {
      if (!this.includes(this.sids, sid)) {
        this.sids.push(sid);
        this.putFocusNextTick('create-note-add-student-input');
        this.recalculateStudentCount();
      }
    },
    addTopic(topic) {
      this.topics.push(topic);
      this.alertScreenReader(`Added topic '${topic}'`);
    },
    cancel() {
      if (this.noteMode === 'editTemplate') {
        if (this.templateEquals(this, this.editModeObject)) {
          this.discardTemplate();
        } else {
          this.showDiscardTemplateModal = true;
        }
      } else {
        const unsavedChanges = this.trim(this.subject) || this.stripHtmlAndTrim(this.body) || this.size(this.attachments) || this.addedCohorts.length || this.addedCuratedGroups.length;
        if (unsavedChanges || !this.templateEquals(this, this.editModeObject)) {
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
    },
    cancelDiscardTemplate() {
      this.setEditModeObject(undefined);
      this.showDiscardTemplateModal = false;
    },
    createNote() {
      const isBatchMode = this.noteMode === 'batch';
      this.subject = this.trim(this.subject);
      if (this.subject && this.targetStudentCount) {
        this.body = this.trim(this.body);
        this.setNoteMode('saving');
        this.onSubmit();
        const afterNoteCreation = () => {
          this.alertScreenReader(isBatchMode ? `Note created for ${this.targetStudentCount} students.` : "New note saved.");
          this.onSuccessfulCreate();
          this.reset();
        };
        if (isBatchMode) {
          const addedCohortIds = this.map(this.addedCohorts, 'id');
          const addedCuratedGroupIds = this.map(this.addedCuratedGroups, 'id');
          createNoteBatch(
            this.sids,
            this.subject,
            this.body,
            this.topics,
            this.attachments,
            addedCohortIds,
            addedCuratedGroupIds
          ).then(afterNoteCreation);
        } else {
          createNote(this.sids[0], this.subject, this.body, this.topics, this.attachments).then(afterNoteCreation);
        }
      }
    },
    createTemplate(title) {
      this.showCreateTemplateModal = false;
      createNoteTemplate(title, this.subject, this.body || '', this.topics, this.attachments).then(template => {
        this.alertScreenReader(`Template ${template.label} created`);
      });
    },
    deleteNoteTemplate(templateId) {
      this.deleteTemplateId = templateId;
    },
    deleteTemplate() {
      deleteNoteTemplate(this.deleteTemplateId).then(() => {
        this.deleteTemplateId = null;
      })
    },
    discardNote() {
      this.showDiscardNoteModal = false;
      this.reset();
      this.alertScreenReader("Cancelled create new note");
    },
    discardTemplate() {
      this.showDiscardTemplateModal = false;
      this.reset(this.initialMode === 'batch' ? 'batch' : 'advanced');
      this.alertScreenReader("Cancelled create new template");
    },
    editNoteTemplate(template) {
      this.setNoteMode('editTemplate');
      this.setEditModeObject(template);
    },
    getTemplateTitle(templateId) {
      const template = this.find(this.noteTemplates, ['id', templateId]);
      return this.get(template, 'title');
    },
    loadTemplate(template) {
      this.subject = template.subject;
      this.body = template.body || '';
      this.topics = this.clone(template.topics || []);
      this.attachments = this.clone(template.attachments || []);
      this.alertScreenReader(`Template ${template.title} loaded`);
    },
    maximize() {
      this.setNoteMode('docked');
      this.alertScreenReader("Create note form is visible.");
      this.putFocusNextTick('create-note-subject');
    },
    minimize() {
      this.isMinimizing = true;
      this.setNoteMode('minimized');
      setTimeout(() => this.isMinimizing = false, 300);
      this.alertScreenReader("Create note form minimized.");
    },
    openNewNoteModal() {
      this.setNoteMode(this.initialMode);
      const isBatchMode = this.noteMode === 'batch';
      this.putFocusNextTick(isBatchMode ? 'create-note-add-student-input' : 'create-note-subject');
      this.alertScreenReader(isBatchMode ? 'Create batch note form is open.' : 'Create note form is open');
    },
    recalculateStudentCount() {
      if (this.addedCohorts || this.addedCuratedGroups) {
        const cohortIds = this.map(this.addedCohorts, 'id');
        const curatedGroupIds = this.map(this.addedCuratedGroups, 'id');
        getDistinctStudentCount(this.sids, cohortIds, curatedGroupIds).then(data => {
          this.targetStudentCount = data.count;
        });
      } else {
        this.targetStudentCount = this.sids.length;
      }
    },
    removeAttachment(index) {
      this.attachments.splice(index, 1);
      this.alertScreenReader(`Attachment '${this.attachments[index].name}' removed`);
    },
    removeCohortFromBatch(cohort) {
      this.addedCohorts = this.filterList(this.addedCohorts, c => c.id !== cohort.id);
      this.alertScreenReader(`Cohort '${cohort.name}' removed`);
      this.recalculateStudentCount();
    },
    removeCuratedGroupFromBatch(curatedGroup) {
      this.addedCuratedGroups = this.filterList(this.addedCuratedGroups, c => c.id !== curatedGroup.id);
      this.alertScreenReader(`Curated group '${curatedGroup.name}' removed`);
      this.recalculateStudentCount();
    },
    removeSid(sid) {
      if (this.includes(this.sids, sid)) {
        this.sids = this.filterList(this.sids, existingSid => existingSid !== sid);
        this.putFocusNextTick('create-note-add-student-input');
        this.recalculateStudentCount();
      }
    },
    removeTopic(topic) {
      let index = this.topics.indexOf(topic);
      this.topics.splice(index, 1);
      this.alertScreenReader(`Removed topic '${topic}'`);
    },
    reset(mode) {
      this.setNoteMode(mode);
      this.addedCohorts = [];
      this.addedCuratedGroups = [];
      this.attachments = [];
      this.body = undefined;
      this.sids = this.sid ? [ this.sid ] : [];
      this.subject = undefined;
      this.targetStudentCount = this.sids.length;
      this.topics = [];
    },
    saveAsTemplate() {
      this.showCreateTemplateModal = true;
    },
    updateTemplate() {
      const t = this.editModeObject;
      updateNoteTemplate(t.id, t.subject, t.body || '', t.topics, t.attachments, []);
    }
  }
}
</script>

<style scoped>
.fa-icon-size {
  font-size: 28px;
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
.new-note-header {
  font-size: 24px;
  margin: 0 15px 12px 15px;
}
</style>
