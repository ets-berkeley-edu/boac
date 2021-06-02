<template>
  <div class="align-items-end d-flex flex-wrap mb-1 mt-2 pt-2">
    <div class="flex-grow-1">
      <ModalHeader class="border-bottom-0" header-id="modal-header-note" :text="mode === 'editTemplate' ? 'Edit Template' : 'New Note'" />
    </div>
    <div class="mr-4">
      <b-dropdown
        v-if="mode !== 'editTemplate'"
        id="my-templates-button"
        class="mb-3 ml-0 pb-1"
        :disabled="isSaving || boaSessionExpired"
        right
        text="Templates"
        toggle-class="btn-primary-color-override"
        variant="primary"
        @show="onShowTemplatesMenu"
        @hide="alertScreenReader('Templates menu closed.')"
      >
        <b-dropdown-header v-if="!$_.size(noteTemplates)" id="no-templates-header" class="templates-dropdown-header">
          <div class="font-weight-bolder">Templates</div>
          <div class="templates-dropdown-instructions">
            You have no saved templates.
          </div>
        </b-dropdown-header>
        <b-dropdown-text
          v-for="template in noteTemplates"
          :key="template.id"
        >
          <div class="align-items-center d-flex font-weight-normal justify-content-between text-nowrap">
            <b-link
              :id="`load-note-template-${template.id}`"
              :title="template.title"
              class="pb-0 text-nowrap template-dropdown-title truncate-with-ellipsis"
              @click="loadTemplate(template)"
            >
              {{ template.title }}
            </b-link>
            <div class="align-items-center d-flex ml-3">
              <div class="pl-2">
                <b-btn
                  :id="`btn-rename-note-template-${template.id}`"
                  variant="link"
                  class="p-0"
                  @click="openRenameTemplateModal(template)"
                >
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
                  @click="editTemplate(template)"
                >
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
                  @click="openDeleteTemplateModal(template)"
                >
                  Delete<span class="sr-only"> template {{ template.title }}</span>
                </b-btn>
              </div>
            </div>
          </div>
        </b-dropdown-text>
      </b-dropdown>
    </div>
    <RenameTemplateModal
      v-if="showRenameTemplateModal"
      :show-modal="showRenameTemplateModal"
      :cancel="cancel"
      :rename="renameTemplate"
      :template="targetTemplate"
      :toggle-show="toggleShowRenameTemplateModal"
    />
    <AreYouSureModal
      v-if="showDeleteTemplateModal"
      :function-cancel="cancel"
      :function-confirm="deleteTemplateConfirmed"
      :modal-body="`Are you sure you want to delete the <b>'${$_.get(targetTemplate, 'title')}'</b> template?`"
      :show-modal="showDeleteTemplateModal"
      button-label-confirm="Delete"
      modal-header="Delete Template"
    />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Context from '@/mixins/Context'
import ModalHeader from '@/components/util/ModalHeader'
import NoteEditSession from '@/mixins/NoteEditSession'
import RenameTemplateModal from '@/components/note/create/RenameTemplateModal'
import Util from '@/mixins/Util'
import {deleteNoteTemplate, renameNoteTemplate} from '@/api/note-templates'

export default {
  name: 'CreateNoteHeader',
  components: {AreYouSureModal, ModalHeader, RenameTemplateModal},
  mixins: [Context, NoteEditSession, Util],
  props: {
    cancelPrimaryModal: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    showDeleteTemplateModal: false,
    showRenameTemplateModal: false,
    targetTemplate: undefined
  }),
  methods: {
    cancel() {
      this.showDeleteTemplateModal = false
      this.showRenameTemplateModal = false
      this.targetTemplate = null
      this.alertScreenReader('Cancelled')
      this.$putFocusNextTick('create-note-subject')
      this.$nextTick(() => {
        this.setFocusLockDisabled(false)
      })
    },
    deleteTemplateConfirmed() {
      deleteNoteTemplate(this.targetTemplate.id).then(() => {
        this.showDeleteTemplateModal = false
        this.targetTemplate = null
        this.alertScreenReader('Template deleted.')
        this.$putFocusNextTick('create-note-subject')
        this.$nextTick(() => {
          this.setFocusLockDisabled(false)
        })
      })
    },
    editTemplate(template) {
      this.setModel(this.$_.cloneDeep(template))
      this.setMode('editTemplate')
      this.$putFocusNextTick('create-note-subject')
      this.alertScreenReader(`Edit template ${template.title}.`)
    },
    loadTemplate(template) {
      this.setModel(this.$_.cloneDeep(template))
      this.$putFocusNextTick('create-note-subject')
      this.alertScreenReader(`Template ${template.title} loaded.`)
    },
    onShowTemplatesMenu() {
      let count = this.$_.size(this.noteTemplates)
      const suffix = count === 1 ? 'one saved template' : `${count || 'no'} saved templates`
      this.alertScreenReader(`Template menu open. You have ${suffix}.`)
    },
    openDeleteTemplateModal(template) {
      this.targetTemplate = template
      this.setFocusLockDisabled(true)
      this.showDeleteTemplateModal = true
      this.alertScreenReader('Delete template modal opened.')
    },
    openRenameTemplateModal(template) {
      this.targetTemplate = template
      this.setFocusLockDisabled(true)
      this.showRenameTemplateModal = true
      this.alertScreenReader('Rename template modal opened.')
    },
    renameTemplate(title) {
      renameNoteTemplate(this.targetTemplate.id, title).then(() => {
        this.targetTemplate = null
        this.showRenameTemplateModal = false
        this.alertScreenReader(`Template renamed '${title}'.`)
        this.$nextTick(() => {
          this.setFocusLockDisabled(false)
        })
      })
    },
    toggleShowRenameTemplateModal(show) {
      this.showRenameTemplateModal = show
      this.setFocusLockDisabled(show)
      this.alertScreenReader(`Dialog ${show ? 'opened' : 'closed'}.`)
    }
  }
}
</script>

<style scoped>
.template-dropdown-title {
  max-width: 200px;
}
.templates-dropdown-header {
  width: 300px;
}
.templates-dropdown-instructions {
  max-width: 300px;
  white-space: normal;
}
</style>
