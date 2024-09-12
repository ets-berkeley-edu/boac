<template>
  <div class="default-margins">
    <div v-if="successMessage" class="mb-3 mr-3 mt-6">
      <v-alert
        id="alert-batch-created"
        aria-live="polite"
        class="font-weight-bold"
        closable
        color="info"
        density="compact"
        fade
        role="alert"
        variant="tonal"
      >
        <span class="font-weight-bold">Success!</span> {{ successMessage }}
      </v-alert>
    </div>
    <h1 id="page-header" class="mb-2 page-section-header">
      Degree Checks
    </h1>
    <div v-if="currentUser.canEditDegreeProgress" class="font-weight-medium mb-3">
      <router-link
        id="degree-check-create-link"
        class="w-25"
        to="/degree/new"
      >
        <div class="align-center d-flex flex-nowrap float-left">
          <v-icon aria-hidden="true" :icon="mdiPlus" size="20" />
          <div class="pl-1 text-no-wrap">
            Create new degree check
          </div>
        </div>
      </router-link>
      <span v-if="size(degreeTemplates)" class="mx-2">|</span>
      <router-link
        v-if="size(degreeTemplates)"
        id="degree-check-batch-link"
        to="/degree/batch"
      >
        <span class="text-no-wrap">Batch degree checks</span>
      </router-link>
    </div>
    <div v-if="!contextStore.loading">
      <div v-if="!degreeTemplates.length">
        There are no degree templates available.
      </div>
      <div v-if="degreeTemplates.length" class="pt-2">
        <v-data-table
          id="degree-checks-table"
          :cell-props="data => {
            const column = data.column.key
            const bgColor = data.index % 2 === 0 ? 'bg-grey-lighten-4' : ''
            const padding = column === 'name' ? 'pl-4 py-2' : 'pl-0'
            const wrap = column === 'name' ? 'overflow-wrap-break-word' : ''
            return {
              id: `td-degree-check-${data.item.id}-column-${column}`,
              class: `${bgColor} font-size-16 ${padding} ${wrap}`
            }
          }"
          density="comfortable"
          disable-sort
          :headers="[
            {key: 'name', headerProps: {class: 'pl-3 manage-degree-checks-column-header'}, width: '60%'},
            {key: 'createdAt', headerProps: {class: 'manage-degree-checks-column-header w-15'}, width: '10%'},
            {key: 'actions', headerProps: {class: 'manage-degree-checks-column-header'}}
          ]"
          :header-props="{class: 'pl-0 text-no-wrap'}"
          hide-default-footer
          :items="degreeTemplates"
          :items-per-page="-1"
          :row-props="data => ({
            id: `tr-degree-check-${data.item.id}`
          })"
        >
          <template #header.name>
            Degree Check
          </template>
          <template #header.createdAt>
            Created
          </template>
          <template #item.name="{item}">
            <div v-if="item.id === get(templateForEdit, 'id')" class="pt-2">
              <v-text-field
                id="rename-template-input"
                v-model="templateForEdit.name"
                :aria-invalid="!templateForEdit.name"
                aria-label="Input template name, 255 characters or fewer"
                aria-required="true"
                class="bg-white w-100"
                :disabled="isRenaming"
                hide-details
                :maxlength="255"
                required
                @keydown.enter="() => templateForEdit.name.length && save()"
                @keyup.esc="cancelEdit"
              />
              <div class="pl-2">
                <span class="font-size-12">255 character limit <span v-if="templateForEdit.name.length">({{ 255 - templateForEdit.name.length }} left)</span></span>
                <span
                  v-if="templateForEdit.name.length === 255"
                  aria-live="polite"
                  class="sr-only"
                  role="alert"
                >
                  Template name cannot exceed 255 characters.
                </span>
              </div>
              <v-alert
                v-if="errorDuringEdit"
                aria-live="polite"
                class="my-2"
                density="compact"
                type="error"
                variant="tonal"
              >
                <span v-html="errorDuringEdit"></span>
              </v-alert>
            </div>
            <div v-if="item.id !== get(templateForEdit, 'id')">
              <router-link
                :id="`degree-check-${item.id}-link`"
                :disabled="isBusy"
                :to="`/degree/${item.id}`"
                v-html="`${item.name}`"
              />
            </div>
          </template>
          <template #item.createdAt="{item}">
            <div v-if="item.id !== get(templateForEdit, 'id')" class="text-no-wrap">
              {{ DateTime.fromISO(item.createdAt).toFormat('DD') }}
            </div>
          </template>
          <template #item.actions="{item}">
            <div v-if="item.id === get(templateForEdit, 'id')" class="d-flex h-100 justify-end pt-4">
              <ProgressButton
                id="confirm-rename-btn"
                :action="save"
                color="primary"
                :disabled="isRenaming || !templateForEdit.name.trim() || !!errorDuringEdit"
                :in-progress="isRenaming"
                :text="isRenaming ? 'Saving...' : 'Rename'"
              />
              <v-btn
                id="rename-cancel-btn"
                class="rename-btn ml-2"
                :disabled="isRenaming"
                variant="text"
                text="Cancel"
                @click="cancelEdit"
              />
            </div>
            <div v-if="item.id !== get(templateForEdit, 'id')" class="align-center d-flex flex-wrap justify-end">
              <v-btn
                :id="`degree-check-${item.id}-print-link`"
                :disabled="isBusy"
                color="primary"
                target="_blank"
                variant="text"
                width="60"
                :to="`/degree/${item.id}/print`"
              >
                Print
                <span class="sr-only">{{ item.name }} (will open new browser tab)</span>
              </v-btn>
              <div v-if="currentUser.canEditDegreeProgress">
                <span class="separator" role="separator">|</span>
                <v-btn
                  :id="`degree-check-${item.id}-rename-btn`"
                  color="primary"
                  :disabled="isBusy"
                  variant="text"
                  width="80"
                  @click="() => edit(item)"
                >
                  Rename<span class="sr-only"> {{ item.name }}</span>
                </v-btn>
              </div>
              <div v-if="currentUser.canEditDegreeProgress">
                <span class="separator" role="separator">|</span>
                <v-btn
                  :id="`degree-check-${item.id}-copy-btn`"
                  color="primary"
                  :disabled="isBusy"
                  variant="text"
                  width="50"
                  @click="openCreateCloneModal(item)"
                >
                  Copy<span class="sr-only"> {{ item.name }}</span>
                </v-btn>
              </div>
              <div v-if="currentUser.canEditDegreeProgress">
                <span class="separator" role="separator">|</span>
                <v-btn
                  :id="`degree-check-${item.id}-delete-btn`"
                  color="primary"
                  :disabled="isBusy"
                  variant="text"
                  width="70"
                  @click="showDeleteModal(item)"
                  @keydown.enter.prevent="showDeleteModal(item)"
                >
                  Delete<span class="sr-only"> {{ item.name }}</span>
                </v-btn>
              </div>
            </div>
          </template>
        </v-data-table>
      </div>
    </div>
    <AreYouSureModal
      v-model="isDeleting"
      button-label-confirm="Delete"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      modal-header="Delete Degree"
      :text="deleteModalBody"
    />
    <CloneTemplateModal
      v-if="templateToClone"
      :after-create="afterClone"
      :cancel="cloneCanceled"
      :template-to-clone="templateToClone"
    />
  </div>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import CloneTemplateModal from '@/components/degree/CloneTemplateModal'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {clone, filter as _filter, get, map, size} from 'lodash'
import {computed, onMounted, ref} from 'vue'
import {DateTime} from 'luxon'
import {deleteDegreeTemplate, getDegreeTemplates, updateDegreeTemplate} from '@/api/degree'
import {mdiPlus} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'
import ProgressButton from '@/components/util/ProgressButton.vue'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser

const deleteModalBody = ref(undefined)
const degreeTemplates = ref(undefined)
const isBusy = ref(false)
const isDeleting = ref(false)
const isRenaming = ref(false)
const successMessage = ref(useRoute().query.m)
const templateForDelete = ref(undefined)
const templateForEdit = ref(undefined)
const templateToClone = ref(undefined)

const errorDuringEdit = computed(() => {
  const template = templateForEdit.value
  const exists = template && !isNameAvailable(template.name, template.id)
  return exists ? `A degree named <span class="font-weight-500">${template.name}</span> already exists. Please choose a different name.` : null
})

contextStore.loadingStart()

onMounted(() => {
  getDegreeTemplates().then(data => {
    degreeTemplates.value = data
    contextStore.loadingComplete()
    alertScreenReader('Managing Degree Checks loaded')
  })
})

const afterClone = clone => {
  templateToClone.value = null
  getDegreeTemplates().then(data => {
    degreeTemplates.value = data
    isBusy.value = false
    alertScreenReader('Degree copy is complete.')
    putFocusNextTick(`degree-check-${clone.id}-link`)
  })
}

const cancelEdit = () => {
  putFocusNextTick(`degree-check-${templateForEdit.value.id}-rename-btn`)
  templateForEdit.value = null
  isBusy.value = false
  alertScreenReader('Canceled')
}

const cloneCanceled = () => {
  putFocusNextTick(`degree-check-${templateToClone.value.id}-copy-btn`)
  templateToClone.value = null
  isBusy.value = false
  alertScreenReader('Copy canceled.')
}

const deleteCanceled = () => {
  putFocusNextTick(`degree-check-${templateForDelete.value.id}-delete-btn`)
  deleteModalBody.value = templateForDelete.value = null
  isBusy.value = isDeleting.value = false
  alertScreenReader('Canceled. Nothing deleted.')
}

const deleteConfirmed = () => {
  return deleteDegreeTemplate(templateForDelete.value.id).then(getDegreeTemplates).then(data => {
    degreeTemplates.value = data
    alertScreenReader(`${templateForDelete.value.name} deleted.`)
    putFocusNextTick('page-header')
    deleteModalBody.value = templateForDelete.value = null
    isBusy.value = isDeleting.value = false
  })
}

const edit = template => {
  alertScreenReader(`Rename ${template.name}`)
  templateForEdit.value = clone(template)
  isBusy.value = true
  putFocusNextTick('rename-template-input')
}

const isNameAvailable = (name, ignoreTemplateId=null) => {
  const lower = name.trim().toLowerCase()
  const templates = ignoreTemplateId ? _filter(degreeTemplates.value, t => t.id !== ignoreTemplateId) : degreeTemplates.value
  return map(templates, 'name').findIndex(t => t.toLowerCase() === lower) === -1
}

const openCreateCloneModal = template => {
  alertScreenReader('Create a copy.')
  templateToClone.value = template
  isBusy.value = true
}

const save = () => {
  isRenaming.value = true
  const name = templateForEdit.value.name.trim()
  updateDegreeTemplate(templateForEdit.value.id, name).then(() => {
    const templateId = templateForEdit.value.id
    templateForEdit.value = null
    getDegreeTemplates().then(data => {
      degreeTemplates.value = data
      isBusy.value = false
      isRenaming.value = false
      putFocusNextTick(`degree-check-${templateId}-rename-btn`)
      alertScreenReader(`Saved changes to template ${name}`)
    })
  })
}

const showDeleteModal = template => {
  deleteModalBody.value = `Are you sure you want to delete <b>"${template.name}"</b>?`
  alertScreenReader('Please confirm delete.')
  templateForDelete.value = template
  isBusy.value = isDeleting.value = true
}
</script>

<style>
#degree-checks-table table {
  border-collapse: collapse;
  table-layout: fixed;
  width: 100%;
}
.manage-degree-checks-column-header {
  color: #666;
  font-weight: 700 !important;
  height: 30px !important;
}
</style>

<style scoped>
.rename-btn {
  height: 36px;
}
.separator {
  color: #ccc;
}
</style>
