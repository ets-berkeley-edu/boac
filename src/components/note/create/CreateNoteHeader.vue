<template>
  <div :class="{'mt-2': undocked}" class="d-flex flex-wrap align-items-end pt-2 mb-1">
    <div class="flex-grow-1 new-note-header font-weight-bolder">
      <span v-if="mode === 'editTemplate'">Edit Template</span>
      <span v-if="mode !== 'editTemplate'">New Note</span>
    </div>
    <div v-if="undocked" class="mr-4">
      <b-dropdown
        id="my-templates-button"
        v-if="mode !== 'editTemplate'"
        :disabled="isSaving"
        text="Templates"
        aria-label="Select a note template"
        variant="primary"
        class="mb-2 ml-0"
        right>
        <b-dropdown-header id="no-templates-header" v-if="!size(noteTemplates)" class="templates-dropdown-header">
          <div class="font-weight-bolder">Templates</div>
          <div class="templates-dropdown-instructions">
            You have no saved templates.
          </div>
        </b-dropdown-header>
        <b-dropdown-text
          v-for="template in noteTemplates"
          :key="template.id">
          <div class="align-items-center d-flex font-weight-normal justify-content-between text-nowrap">
            <b-link
              :id="`load-note-template-${template.id}`"
              :title="template.title"
              @click="loadTemplate(template)"
              class="pb-0 text-nowrap template-dropdown-title truncate-with-ellipsis">
              {{ template.title }}
            </b-link>
            <div class="align-items-center d-flex ml-3">
              <div class="pl-2">
                <b-btn
                  :id="`btn-rename-note-template-${template.id}`"
                  @click="openRenameTemplateModal(template)"
                  variant="link"
                  class="p-0">
                  Rename<span class="sr-only"> template {{ template.title }}</span>
                </b-btn>
              </div>
              <div class="pl-1 pr-1">
                |
              </div>
              <div>
                <b-btn
                  :id="`btn-edit-note-template-${template.id}`"
                  @click="editTemplate(template)"
                  variant="link"
                  class="p-0">
                  Edit<span class="sr-only"> template {{ template.title }}</span>
                </b-btn>
              </div>
              <div class="pl-1 pr-1">
                |
              </div>
              <div>
                <b-btn
                  :id="`btn-delete-note-template-${template.id}`"
                  @click="openDeleteTemplateModal(template)"
                  variant="link"
                  class="p-0">
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
        <label for="minimize-new-note-modal" class="sr-only">Minimize the create note dialog box</label>
        <b-btn
          id="minimize-new-note-modal"
          @click.prevent="minimize()"
          variant="link"
          class="pr-2">
          <span class="sr-only">Minimize</span>
          <font-awesome icon="window-minimize" class="minimize-icon text-dark" />
        </b-btn>
      </div>
      <div class="pr-2">
        <label for="cancel-new-note-modal" class="sr-only">Cancel the create-note form</label>
        <b-btn
          id="cancel-new-note-modal"
          @click.prevent="cancelPrimaryModal()"
          variant="link"
          class="pl-1 pb-1">
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
      :function-cancel="cancel"
      :function-confirm="deleteTemplateConfirmed"
      :modal-body="`Are you sure you want to delete the <b>'${get(targetTemplate, 'title')}'</b> template?`"
      :show-modal="showDeleteTemplateModal"
      button-label-confirm="Delete"
      modal-header="Delete Template" />
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
