<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner />
    <h1 id="page-header" class="page-section-header pl-1">
      Managing Degree Checks
    </h1>
    <div class="pb-3">
      <router-link
        v-if="$currentUser.canEditDegreeProgress"
        id="degree-check-create-link"
        class="w-25"
        to="/degree/new"
      >
        <div class="align-items-center d-flex justify-content-between">
          <div class="pr-2 text-nowrap">
            Create new degree check
          </div>
          <div>
            <font-awesome icon="plus" />
          </div>
        </div>
      </router-link>
    </div>
    <div v-if="!loading">
      <div v-if="degreeTemplates.length">
        <b-table-lite
          id="degree-checks-table"
          :fields="[
            {key: 'name', label: 'Degree Check', tdClass: 'align-middle', thClass: 'w-50'},
            {key: 'createdAt', label: 'Created', tdClass: 'align-middle'},
            {key: 'actions', label: '', thClass: 'w-40'}
          ]"
          :items="degreeTemplates"
          borderless
          fixed
          hover
          small
          stacked="md"
          striped
          thead-class="sortable-table-header text-nowrap"
        >
          <template #cell(name)="row">
            <div
              v-if="row.item.id === $_.get(templateForEdit, 'id')"
              class="align-items-center d-flex flex-wrap justify-content-between mt-2 rename-template"
            >
              <div class="flex-grow-1 mr-2">
                <div>
                  <input
                    id="rename-template-input"
                    v-model="templateForEdit.name"
                    :aria-invalid="!templateForEdit.name"
                    class="rename-input text-dark p-2 w-100"
                    aria-label="Input template name, 255 characters or fewer"
                    aria-required="true"
                    maxlength="255"
                    required
                    type="text"
                    @keypress.enter="() => templateForEdit.name.length && save()"
                    @keyup.esc="cancelEdit"
                  />
                </div>
                <div class="pl-2">
                  <span class="faint-text font-size-12">255 character limit <span v-if="templateForEdit.name.length">({{ 255 - templateForEdit.name.length }} left)</span></span>
                  <span
                    v-if="templateForEdit.name.length === 255"
                    aria-live="polite"
                    class="sr-only"
                    role="alert"
                  >
                    Template name cannot exceed 255 characters.
                  </span>
                </div>
              </div>
              <div class="align-items-center d-flex pb-3 mb-2 mr-2">
                <b-btn
                  id="confirm-rename-btn"
                  :disabled="!templateForEdit.name || !!errorDuringEdit"
                  class="btn-primary-color-override rename-btn"
                  variant="primary"
                  size="sm"
                  @click.prevent="save"
                >
                  Rename
                </b-btn>
                <b-btn
                  id="rename-cancel-btn"
                  class="rename-btn"
                  variant="link"
                  size="sm"
                  @click="cancelEdit"
                >
                  Cancel
                </b-btn>
              </div>
              <div v-if="errorDuringEdit" class="error-message-container mb-3 ml-2 mt-2 p-2">
                <span v-html="errorDuringEdit"></span>
              </div>
            </div>
            <div v-if="row.item.id !== $_.get(templateForEdit, 'id')">
              <router-link
                :id="`degree-check-${row.item.id}-link`"
                :disabled="isBusy"
                :to="`degree/${row.item.id}`"
                v-html="`${row.item.name}`"
              />
            </div>
          </template>
          <template #cell(createdAt)="row">
            <div v-if="row.item.id !== $_.get(templateForEdit, 'id')">
              {{ row.item.createdAt | moment('MMM D, YYYY') }}
            </div>
          </template>
          <template #cell(actions)="row">
            <div class="align-right w-100">
              <div v-if="row.item.id !== $_.get(templateForEdit, 'id')" class="align-items-center d-flex flex-wrap">
                <div>
                  <router-link
                    :id="`degree-check-${row.item.id}-print-link`"
                    class="p-1"
                    :disabled="isBusy"
                    :to="`degree/print/${row.item.id}`"
                  >
                    Print
                  </router-link>
                </div>
                <div v-if="$currentUser.canEditDegreeProgress">
                  <span class="separator">|</span>
                  <b-btn
                    v-if="$currentUser.canEditDegreeProgress"
                    :id="`degree-check-${row.index}-rename-btn`"
                    class="p-1"
                    :disabled="isBusy"
                    variant="link"
                    @click="edit(row.item)"
                  >
                    Rename
                  </b-btn>
                </div>
                <div v-if="$currentUser.canEditDegreeProgress">
                  <span class="separator">|</span>
                  <b-btn
                    :id="`degree-check-${row.index}-copy-btn`"
                    class="p-1"
                    :disabled="isBusy"
                    variant="link"
                    @click="openCreateCloneModal(row.item)"
                  >
                    Copy
                  </b-btn>
                </div>
                <div v-if="$currentUser.canEditDegreeProgress">
                  <span class="separator">|</span>
                  <b-btn
                    v-if="$currentUser.canEditDegreeProgress"
                    :id="`degree-check-${row.index}-delete-btn`"
                    class="p-1"
                    :disabled="isBusy"
                    variant="link"
                    @click="showDeleteModal(row.item)"
                    @keypress.enter="showDeleteModal(row.item)"
                  >
                    Delete
                  </b-btn>
                </div>
              </div>
            </div>
          </template>
        </b-table-lite>
      </div>
    </div>
    <AreYouSureModal
      v-if="templateForDelete"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :modal-body="deleteModalBody"
      :show-modal="!!templateForDelete"
      button-label-confirm="Delete"
      modal-header="Delete Degree"
    />
    <CloneTemplateModal
      v-if="templateToClone"
      :after-create="afterClone"
      :cancel="cloneCanceled"
      :template-to-clone="templateToClone"
    />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import CloneTemplateModal from '@/components/degree/CloneTemplateModal'
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {deleteDegreeTemplate, getDegreeTemplates, updateDegreeTemplate} from '@/api/degree'

export default {
  name: 'ManageDegreeChecks',
  components: {AreYouSureModal, CloneTemplateModal, Spinner},
  mixins: [Context, Loading, Util],
  data: () => ({
    deleteModalBody: undefined,
    degreeTemplates: undefined,
    isBusy: false,
    templateForDelete: undefined,
    templateForEdit: undefined,
    templateToClone: undefined
  }),
  computed: {
    errorDuringEdit() {
      if (this.templateForEdit && !this.isNameAvailable(this.templateForEdit.name, this.templateForEdit.id)) {
        return `A degree named <span class="font-weight-500">${this.templateForEdit.name}</span> already exists. Please choose a different name.`
      } else {
        return null
      }
    }
  },
  mounted() {
    getDegreeTemplates().then(data => {
      this.degreeTemplates = data
      this.loaded('Degree Checks loaded')
    })
  },
  methods: {
    afterClone(clone) {
      this.templateToClone = null
      getDegreeTemplates().then(data => {
        this.degreeTemplates = data
        this.isBusy = false
        this.$announcer.polite('Degree copy is complete.')
        this.putFocusNextTick(`degree-check-${clone.id}-link`)
      })
    },
    cancelEdit() {
      this.putFocusNextTick(`degree-check-${this.templateForEdit.id}-link`)
      this.templateForEdit = null
      this.isBusy = false
      this.$announcer.polite('Canceled')
    },
    cloneCanceled() {
      this.putFocusNextTick(`degree-check-${this.templateToClone.id}-link`)
      this.templateToClone = null
      this.isBusy = false
      this.$announcer.polite('Copy canceled.')
    },
    deleteCanceled() {
      this.putFocusNextTick(`degree-check-${this.templateForDelete.id}-link`)
      this.deleteModalBody = this.templateForDelete = null
      this.isBusy = false
      this.$announcer.polite('Canceled. Nothing deleted.')
    },
    deleteConfirmed() {
      deleteDegreeTemplate(this.templateForDelete.id).then(() => {
        getDegreeTemplates().then(data => {
          this.degreeTemplates = data
          this.$announcer.polite(`${this.templateForDelete.name} deleted.`)
          this.putFocusNextTick('page-header')
          this.deleteModalBody = this.templateForDelete = null
          this.isBusy = false
        })
      })
    },
    edit(template) {
      this.$announcer.polite(`Rename ${template.name}`)
      this.templateForEdit = this.$_.clone(template)
      this.isBusy = true
      this.putFocusNextTick('rename-template-input')
    },
    isNameAvailable(name, ignoreTemplateId=null) {
      const lower = name.trim().toLowerCase()
      const templates = ignoreTemplateId ? this.$_.filter(this.degreeTemplates, t => t.id !== ignoreTemplateId) : this.degreeTemplates
      return this.$_.map(templates, 'name').findIndex(t => t.toLowerCase() === lower) === -1
    },
    openCreateCloneModal(template) {
      this.$announcer.polite('Create a copy.')
      this.templateToClone = template
      this.isBusy = true
    },
    save() {
      updateDegreeTemplate(this.templateForEdit.id, this.templateForEdit.name).then(() => {
        const templateId = this.templateForEdit.id
        this.templateForEdit = null
        getDegreeTemplates().then(data => {
          this.degreeTemplates = data
          this.$announcer.polite('Template updated')
          this.isBusy = false
          this.putFocusNextTick(`degree-check-${templateId}-link`)
        })
      })
    },
    showDeleteModal(template) {
      this.deleteModalBody = `Are you sure you want to delete <b>"${template.name}"</b>?`
      this.$announcer.polite('Please confirm delete.')
      this.templateForDelete = template
      this.isBusy = true
    }
  }
}
</script>

<style scoped>
.rename-input {
  box-sizing: border-box;
  border: 2px solid #ccc;
  border-radius: 4px;
}
.rename-template {
  overflow: visible;
  width: 800px;
  z-index: 100;
}
.separator {
  color: #ccc;
}
</style>
