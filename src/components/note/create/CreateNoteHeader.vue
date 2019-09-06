<template>
  <div class="d-flex flex-wrap align-items-end pt-2 mb-1" :class="{'mt-2': undocked}">
    <div class="flex-grow-1 new-note-header font-weight-bolder">
      <span v-if="mode === 'editTemplate'">Edit Template</span>
      <span v-if="mode !== 'editTemplate'">New Note</span>
    </div>
    <div v-if="undocked" class="mr-4">
      <b-dropdown
        v-if="mode !== 'editTemplate'"
        id="my-templates-button"
        :disabled="isSaving"
        text="Templates"
        aria-label="Select a note template"
        variant="primary"
        class="mb-2 ml-0"
        right>
        <b-dropdown-header v-if="!size(noteTemplates)" id="no-templates-header" class="templates-dropdown-header">
          <div class="font-weight-bolder">Templates</div>
          <div class="templates-dropdown-instructions">
            You have no saved templates.
          </div>
        </b-dropdown-header>
        <b-dropdown-text
          v-for="template in noteTemplates"
          :key="template.id">
          <div class="align-items-center d-flex justify-content-between text-nowrap">
            <b-link
              :id="`load-note-template-${template.id}`"
              class="pb-0 text-nowrap template-dropdown-title truncate-with-ellipsis"
              :title="template.title"
              @click="loadTemplate(template)">
              {{ template.title }}
            </b-link>
            <div class="align-items-center d-flex ml-3">
              <div class="pl-2">
                <b-btn
                  :id="`btn-rename-note-template-${template.id}`"
                  variant="link"
                  class="p-0"
                  @click="openRenameTemplateModal(template)">
                  Rename<span class="sr-only"> template {{ template.title }}</span>
                </b-btn>
              </div>
              <div class="pl-1 pr-1">
                |
              </div>
              <div>
                <b-btn
                  :id="`btn-edit-note-template-${template.id}`"
                  variant="link"
                  class="p-0"
                  @click="editTemplate(template)">
                  Edit<span class="sr-only"> template {{ template.title }}</span>
                </b-btn>
              </div>
              <div class="pl-1 pr-1">
                |
              </div>
              <div>
                <b-btn
                  :id="`btn-delete-note-template-${template.id}`"
                  variant="link"
                  class="p-0"
                  @click="openDeleteTemplateModal(template)">
                  Delete<span class="sr-only"> template {{ template.title }}</span>
                </b-btn>
              </div>
            </div>
          </div>
        </b-dropdown-text>
      </b-dropdown>
    </div>
    <div v-if="!undocked" class="d-flex">
      <div class="pr-0">
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
      <div class="pr-2">
        <label id="cancel-button-label" class="sr-only">Cancel the create-note form</label>
        <b-btn
          id="cancel-new-note-modal"
          variant="link"
          aria-labelledby="cancel-button-label"
          class="pl-1 pb-1"
          @click.prevent="cancelPrimaryModal()">
          <span class="sr-only">Cancel</span>
          <font-awesome icon="times" class="fa-icon-size text-dark" />
        </b-btn>
      </div>
    </div>
    <RenameTemplateModal
      v-if="showRenameTemplateModal"
      :show-modal="showRenameTemplateModal"
      :cancel="cancel"
      :rename="renameTemplate"
      :template="targetTemplate"
      :toggle-show="toggleShowRenameTemplateModal" />
    <AreYouSureModal
      v-if="showDeleteTemplateModal"
      button-label-confirm="Delete"
      :function-cancel="cancel"
      :function-confirm="deleteTemplateConfirmed"
      :modal-body="`Are you sure you want to delete the <b>'${get(targetTemplate, 'title')}'</b> template?`"
      modal-header="Delete Template"
      :show-modal="showDeleteTemplateModal" />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal';
import Context from '@/mixins/Context';
import NoteEditSession from '@/mixins/NoteEditSession';
import RenameTemplateModal from '@/components/note/create/RenameTemplateModal'
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import {deleteNoteTemplate, renameNoteTemplate} from '@/api/note-templates';

export default {
  name: 'CreateNoteHeader',
  components: {AreYouSureModal, RenameTemplateModal},
  mixins: [Context, NoteEditSession, UserMetadata, Util],
  props: {
    cancelPrimaryModal: {
      required: true,
      type: Function
    },
    minimize: {
      required: true,
      type: Function
    },
    undocked: {
      required: true,
      type: Boolean
    }
  },
  data: () => ({
    showDeleteTemplateModal: false,
    showRenameTemplateModal: false,
    targetTemplate: undefined
  }),
  methods: {
    cancel() {
      this.showDeleteTemplateModal = false;
      this.showRenameTemplateModal = false;
      this.targetTemplate = null;
      this.putFocusNextTick('create-note-subject');
      this.setFocusLockDisabled(false);
    },
    deleteTemplateConfirmed() {
      deleteNoteTemplate(this.targetTemplate.id).then(() => {
        this.showDeleteTemplateModal = false;
        this.setFocusLockDisabled(false);
        this.targetTemplate = null;
        this.putFocusNextTick('create-note-subject');
      })
    },
    editTemplate(template) {
      this.setModel(this.cloneDeep(template));
      this.setMode('editTemplate');
      this.putFocusNextTick('create-note-subject');
    },
    loadTemplate(template) {
      this.setModel(this.cloneDeep(template));
      this.putFocusNextTick('create-note-subject');
      this.alertScreenReader(`Template ${template.title} loaded`);
    },
    openDeleteTemplateModal(template) {
      this.targetTemplate = template;
      this.setFocusLockDisabled(true);
      this.showDeleteTemplateModal = true;
    },
    openRenameTemplateModal(template) {
      this.targetTemplate = template;
      this.setFocusLockDisabled(true);
      this.showRenameTemplateModal = true;
    },
    renameTemplate(title) {
      renameNoteTemplate(this.targetTemplate.id, title).then(() => {
        this.targetTemplate = null;
        this.showRenameTemplateModal = false;
        this.setFocusLockDisabled(false);
      });
    },
    toggleShowRenameTemplateModal(show) {
      this.showRenameTemplateModal = show;
      this.setFocusLockDisabled(show);
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
.new-note-header {
  font-size: 24px;
  margin: 0 15px 6px 15px;
}
.templates-dropdown-instructions {
  max-width: 300px;
  white-space: normal;
}
.templates-dropdown-header {
  width: 300px;
}
.template-dropdown-title {
  max-width: 200px;
}
</style>
