<template>
  <div>
    <v-alert
      id="alert-batch-created"
      v-model="successMessage"
      aria-live="polite"
      class="align-center w-100"
      closable
      fade
      role="alert"
      variant="outlined"
    >
      <span class="font-weight-700">Success!</span> {{ successMessage }}
    </v-alert>
    <h1 id="page-header" class="page-section-header">
      Degree Checks
    </h1>
    <div v-if="currentUser.canEditDegreeProgress" class="pb-3 w-10">
      <router-link
        id="degree-check-create-link"
        class="w-25"
        to="/degree/new"
      >
        <div class="align-center d-inline-flex flex-nowrap">
          <div class="order-2 text-no-wrap">
            Create new degree check
          </div>
          <div class="order-1 pr-2">
            <v-icon :icon="mdiPlus" />
          </div>
        </div>
      </router-link>
      <span v-if="_size(degreeTemplates)" class="p-2">|</span>
      <router-link
        v-if="_size(degreeTemplates)"
        id="degree-check-batch-link"
        class="w-25"
        to="/degree/batch"
      >
        <span class="text-no-wrap">Batch degree checks</span>
      </router-link>
    </div>
    <div v-if="!loading">
      <div v-if="!degreeTemplates.length">
        There are no degree templates available.
      </div>
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
          thead-class="text-no-wrap"
        >
          <template #cell(name)="row">
            <div
              v-if="row.item.id === _get(templateForEdit, 'id')"
              class="align-center d-flex flex-wrap justify-space-between mt-2 rename-template"
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
                  <span class="text-grey font-size-12">255 character limit <span v-if="templateForEdit.name.length">({{ 255 - templateForEdit.name.length }} left)</span></span>
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
              <div class="align-center d-flex pb-3 mb-2 mr-2">
                <b-btn
                  id="confirm-rename-btn"
                  :disabled="!templateForEdit.name.trim() || !!errorDuringEdit"
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
            <div v-if="row.item.id !== _get(templateForEdit, 'id')">
              <router-link
                :id="`degree-check-${row.item.id}-link`"
                :disabled="isBusy"
                :to="`/degree/${row.item.id}`"
                v-html="`${row.item.name}`"
              />
            </div>
          </template>
          <template #cell(createdAt)="row">
            <div v-if="row.item.id !== _get(templateForEdit, 'id')">
              {{ DateTime.fromJSDate(row.item.createdAt).toFormat('MMM D, YYYY') }}
            </div>
          </template>
          <template #cell(actions)="row">
            <div class="align-right w-100">
              <div v-if="row.item.id !== _get(templateForEdit, 'id')" class="align-center d-flex flex-wrap">
                <div>
                  <router-link
                    :id="`degree-check-${row.item.id}-print-link`"
                    class="p-1"
                    :disabled="isBusy"
                    target="_blank"
                    :to="`/degree/${row.item.id}/print`"
                  >
                    Print
                    <span class="sr-only">{{ row.item.name }} (will open new browser tab)</span>
                  </router-link>
                </div>
                <div v-if="currentUser.canEditDegreeProgress">
                  <span class="separator">|</span>
                  <b-btn
                    :id="`degree-check-${row.index}-rename-btn`"
                    class="p-1"
                    :disabled="isBusy"
                    variant="link"
                    @click="edit(row.item)"
                  >
                    Rename<span class="sr-only"> {{ row.item.name }}</span>
                  </b-btn>
                </div>
                <div v-if="currentUser.canEditDegreeProgress">
                  <span class="separator">|</span>
                  <b-btn
                    :id="`degree-check-${row.index}-copy-btn`"
                    class="p-1"
                    :disabled="isBusy"
                    variant="link"
                    @click="openCreateCloneModal(row.item)"
                  >
                    Copy<span class="sr-only"> {{ row.item.name }}</span>
                  </b-btn>
                </div>
                <div v-if="currentUser.canEditDegreeProgress">
                  <span class="separator">|</span>
                  <b-btn
                    :id="`degree-check-${row.index}-delete-btn`"
                    class="p-1"
                    :disabled="isBusy"
                    variant="link"
                    @click="showDeleteModal(row.item)"
                    @keypress.enter="showDeleteModal(row.item)"
                  >
                    Delete<span class="sr-only"> {{ row.item.name }}</span>
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
      :show-modal="!!templateForDelete"
      button-label-confirm="Delete"
      modal-header="Delete Degree"
    >
      {{ deleteModalBody }}
    </AreYouSureModal>
    <CloneTemplateModal
      v-if="templateToClone"
      :after-create="afterClone"
      :cancel="cloneCanceled"
      :template-to-clone="templateToClone"
    />
  </div>
</template>

<script setup>
import {mdiPlus} from '@mdi/js'
</script>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import CloneTemplateModal from '@/components/degree/CloneTemplateModal'
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'
import {deleteDegreeTemplate, getDegreeTemplates, updateDegreeTemplate} from '@/api/degree'
import {DateTime} from 'luxon'

export default {
  name: 'ManageDegreeChecks',
  components: {AreYouSureModal, CloneTemplateModal},
  mixins: [Context, DegreeEditSession, Util],
  data: () => ({
    deleteModalBody: undefined,
    degreeTemplates: undefined,
    isBusy: false,
    successMessage: undefined,
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
      this.successMessage = this.$route.query.m
      this.loadingComplete()
      alertScreenReader('Managing Degree Checks loaded')
    })
  },
  methods: {
    afterClone(clone) {
      this.templateToClone = null
      getDegreeTemplates().then(data => {
        this.degreeTemplates = data
        this.isBusy = false
        alertScreenReader('Degree copy is complete.')
        this.putFocusNextTick(`degree-check-${clone.id}-link`)
      })
    },
    cancelEdit() {
      this.putFocusNextTick(`degree-check-${this.templateForEdit.id}-link`)
      this.templateForEdit = null
      this.isBusy = false
      alertScreenReader('Canceled')
    },
    cloneCanceled() {
      this.putFocusNextTick(`degree-check-${this.templateToClone.id}-link`)
      this.templateToClone = null
      this.isBusy = false
      alertScreenReader('Copy canceled.')
    },
    deleteCanceled() {
      this.putFocusNextTick(`degree-check-${this.templateForDelete.id}-link`)
      this.deleteModalBody = this.templateForDelete = null
      this.isBusy = false
      alertScreenReader('Canceled. Nothing deleted.')
    },
    deleteConfirmed() {
      return deleteDegreeTemplate(this.templateForDelete.id).then(getDegreeTemplates).then(data => {
        this.degreeTemplates = data
        alertScreenReader(`${this.templateForDelete.name} deleted.`)
        this.putFocusNextTick('page-header')
        this.deleteModalBody = this.templateForDelete = null
        this.isBusy = false
      })
    },
    edit(template) {
      alertScreenReader(`Rename ${template.name}`)
      this.templateForEdit = this._clone(template)
      this.isBusy = true
      this.putFocusNextTick('rename-template-input')
    },
    isNameAvailable(name, ignoreTemplateId=null) {
      const lower = name.trim().toLowerCase()
      const templates = ignoreTemplateId ? this._filter(this.degreeTemplates, t => t.id !== ignoreTemplateId) : this.degreeTemplates
      return this._map(templates, 'name').findIndex(t => t.toLowerCase() === lower) === -1
    },
    openCreateCloneModal(template) {
      alertScreenReader('Create a copy.')
      this.templateToClone = template
      this.isBusy = true
    },
    save() {
      updateDegreeTemplate(this.templateForEdit.id, this.templateForEdit.name.trim()).then(() => {
        const templateId = this.templateForEdit.id
        this.templateForEdit = null
        getDegreeTemplates().then(data => {
          this.degreeTemplates = data
          alertScreenReader('Template updated')
          this.isBusy = false
          this.putFocusNextTick(`degree-check-${templateId}-link`)
        })
      })
    },
    showDeleteModal(template) {
      this.deleteModalBody = `Are you sure you want to delete <b>"${template.name}"</b>?`
      alertScreenReader('Please confirm delete.')
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
