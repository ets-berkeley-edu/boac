<template>
  <div>
    <div v-if="!degreeTemplates.length">
      There are no {{ mode === 'archived' ? 'archived degree templates.' : 'degree templates available.' }}
    </div>
    <div v-if="degreeTemplates.length" class="pt-2 w-100">
      <v-data-table
        id="degree-checks-table"
        :cell-props="data => {
          const column = data.column.key
          const bgColor = tableRowHighlightId === data.item.id ? 'bg-sky-blue border-b-md border-t-md' : (data.index % 2 === 0 ? 'bg-surface-light' : '')
          const padding = column === 'name' ? 'pl-4 py-2' : 'pl-0 pr-2'
          const wrap = column === 'name' ? 'overflow-wrap-break-word' : ''
          return {
            id: `td-degree-check-${data.item.id}-column-${column}`,
            class: `${bgColor} font-size-16 ${padding} ${wrap}`
          }
        }"
        class="no-scrollbar"
        density="comfortable"
        disable-sort
        :headers="[
          {key: 'name', headerProps: {class: 'pl-3 manage-degree-checks-column-header text-medium-emphasis'}, width: '60%'},
          {key: 'createdAt', headerProps: {class: 'manage-degree-checks-column-header text-medium-emphasis'}, width: '125px'},
          {key: 'actions', headerProps: {class: 'pr-1 manage-degree-checks-column-header text-medium-emphasis'}, width: '40%'}
        ]"
        :header-props="{class: 'pl-0 text-no-wrap', tabindex: undefined}"
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
        <template #header.actions>
          <span class="sr-only">Actions</span>
        </template>
        <template #item.name="{item}">
          <div v-if="templateForEdit && item.id === templateForEdit.id" class="pt-2">
            <v-text-field
              id="rename-template-input"
              v-model="templateForEdit.name"
              :aria-invalid="!templateForEdit.name"
              aria-label="Degree Template name"
              aria-required="true"
              class="bg-white w-100"
              :disabled="isRenaming"
              autocomplete="on"
              hide-details
              :maxlength="255"
              required
              @keydown.enter="() => size(templateForEdit.name) && save()"
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
              <span v-html="errorDuringEdit" />
            </v-alert>
          </div>
          <div v-if="item.id !== get(templateForEdit, 'id')">
            <component
              :is="isBusy ? 'span' : 'router-link'"
              :id="`degree-check-${item.id}-link`"
              :class="{'text-disabled': isBusy}"
              :to="`/degree/${item.id}`"
              v-html="`${item.name}`"
            />
          </div>
        </template>
        <template #item.createdAt="{item}">
          <div
            v-if="item.id !== get(templateForEdit, 'id')"
            class="text-no-wrap"
            :class="{'text-disabled': isBusy}"
          >
            {{ DateTime.fromISO(item.createdAt).toFormat('DD') }}
          </div>
        </template>
        <template #item.actions="{item}">
          <div v-if="templateForEdit && item.id === templateForEdit.id" class="d-flex h-100 justify-end pt-4">
            <ProgressButton
              id="confirm-rename-btn"
              :action="save"
              aria-label="Rename Degree Template"
              color="primary"
              :disabled="isRenaming || !trim(templateForEdit.name) || !!errorDuringEdit"
              :in-progress="isRenaming"
              :text="isRenaming ? 'Saving...' : 'Rename'"
            />
            <v-btn
              id="rename-cancel-btn"
              aria-label="Cancel Rename Degree Template"
              class="ml-2"
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
              class="font-size-14 degree-check-btn"
              color="primary"
              size="x-sm"
              target="_blank"
              variant="text"
              :to="`/degree/${item.id}/print`"
            >
              Print
              <span class="sr-only">{{ item.name }} (opens in new tab)</span>
            </v-btn>
            <div v-if="currentUser.canEditDegreeProgress" class="d-flex align-center">
              <span class="text-disabled" role="separator">|</span>
              <v-btn
                :id="`degree-check-${item.id}-rename-btn`"
                class="font-size-14 degree-check-btn"
                color="primary"
                :disabled="isBusy"
                size="x-sm"
                variant="text"
                @click="() => edit(item)"
              >
                Rename<span class="sr-only"> {{ item.name }}</span>
              </v-btn>
            </div>
            <div v-if="currentUser.canEditDegreeProgress" class="d-flex flex-wrap flex-sm-nowrap justify-end">
              <div class="align-center d-flex">
                <span class="text-disabled" role="separator">|</span>
                <v-btn
                  :id="`degree-check-${item.id}-copy-btn`"
                  class="font-size-14 degree-check-btn"
                  color="primary"
                  :disabled="isBusy"
                  size="x-sm"
                  variant="text"
                  @click="openCreateCloneModal(item)"
                >
                  Copy<span class="sr-only"> {{ item.name }}</span>
                </v-btn>
              </div>
              <div class="align-center d-flex">
                <span class="text-disabled" role="separator">|</span>
                <v-btn
                  :id="`degree-check-${item.id}-${mode}-btn`"
                  class="font-size-14 degree-check-btn"
                  color="primary"
                  :disabled="isBusy"
                  size="x-sm"
                  variant="text"
                  @click="toggleArchivedAt(item)"
                >
                  {{ mode === 'archived' ? 'Unarchive' : 'Archive' }}<span class="sr-only"> {{ item.name }}</span>
                </v-btn>
              </div>
              <div class="align-center d-flex">
                <span class="text-disabled" role="separator">|</span>
                <v-btn
                  :id="`degree-check-${item.id}-delete-btn`"
                  class="font-size-14 degree-check-btn"
                  color="primary"
                  :disabled="isBusy"
                  size="x-sm"
                  variant="text"
                  @click="showDeleteModal(item)"
                  @keydown.enter.prevent="showDeleteModal(item)"
                >
                  Delete<span class="sr-only"> {{ item.name }}</span>
                </v-btn>
              </div>
            </div>
          </div>
        </template>
      </v-data-table>
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

<script lang="ts" setup>
import type {PropType} from 'vue'
import {filter as _filter, clone, findIndex, get, map, size, trim} from 'lodash'
import {computed, ref} from 'vue'
import {DateTime} from 'luxon'
import type {DegreeTemplate} from '@/lib/types'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import CloneTemplateModal from '@/components/degree/CloneTemplateModal.vue'
import ProgressButton from '@/components/util/ProgressButton.vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {
  archiveDegreeTemplate,
  deleteDegreeTemplate,
  unarchiveDegreeTemplate,
  updateDegreeTemplate,
} from '@/api/degree'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  degreeTemplates: {
    required: true,
    type: Array as PropType<DegreeTemplate[]>,
  },
  mode: {
    required: true,
    type: String
  },
  tableRowHighlightId: {
    default: undefined,
    required: false,
    type: Number,
  },
  onUpdateDegreeTemplate: {
    required: true,
    type: Function
  }
})

const currentUser = useContextStore().currentUser
const deleteModalBody = ref<string | undefined>()
const isBusy = ref(false)
const isDeleting = ref(false)
const isRenaming = ref(false)
const templateForDelete = ref<DegreeTemplate | undefined>()
const templateForEdit = ref<DegreeTemplate | undefined>()
const templateToClone = ref<DegreeTemplate | undefined>()

const errorDuringEdit = computed(() => {
  let message: string | null = null
  if (templateForEdit.value) {
    const name = trim(templateForEdit.value.name)
    const exists = !!name && !isNameAvailable(name, templateForEdit.value.id)
    message = exists ? `A degree named <span class="font-weight-500">${name}</span> already exists. Please choose a different name.` : null
  }
  return message
})

const toggleArchivedAt = (degreeTemplate: DegreeTemplate) => {
  const nextFocusId = getNextFocusId(degreeTemplate.id, props.mode)
  const templateName = degreeTemplate.name
  const api = props.mode === 'archived' ? unarchiveDegreeTemplate : archiveDegreeTemplate
  isBusy.value = true
  alertScreenReader(`${props.mode === 'archived' ? 'Unarchiving' : 'Archiving'} degree template`)
  api(degreeTemplate.id).then(data => {
    props.onUpdateDegreeTemplate(data).then(() => {
      isBusy.value = false
      alertScreenReader(`${props.mode === 'archived' ? 'Unarchived' : 'Archived'} ${templateName}`)
      putFocusNextTick(nextFocusId)
    })
  })
}

const afterClone = (clone: DegreeTemplate) => {
  props.onUpdateDegreeTemplate(clone).then(() => {
    templateToClone.value = undefined
    isBusy.value = false
    alertScreenReader('Degree copy is complete.')
    putFocusNextTick(`degree-check-${clone.id}-link`)
  })
}

const cancelEdit = () => {
  if (templateForEdit.value) {
    putFocusNextTick(`degree-check-${templateForEdit.value.id}-rename-btn`)
    templateForEdit.value = undefined
    isBusy.value = false
    alertScreenReader('Canceled')
  }
}

const cloneCanceled = () => {
  if (templateToClone.value) {
    putFocusNextTick(`degree-check-${templateToClone.value.id}-copy-btn`)
    templateToClone.value = undefined
    isBusy.value = false
    alertScreenReader('Canceled copy.')
  }
}

const deleteCanceled = () => {
  if (templateForDelete.value) {
    putFocusNextTick(`degree-check-${templateForDelete.value.id}-delete-btn`)
    deleteModalBody.value = templateForDelete.value = undefined
    isBusy.value = isDeleting.value = false
    alertScreenReader('Canceled. Nothing deleted.')
  }
}

const deleteConfirmed = () => {
  if (templateForDelete.value) {
    const nextFocusId = getNextFocusId(templateForDelete.value.id, 'delete')
    alertScreenReader('Deleting degree template')
    deleteDegreeTemplate(templateForDelete.value.id).then(() => {
      props.onUpdateDegreeTemplate(templateForDelete.value).then(() => {
        alertScreenReader(`Deleted "${get(templateForDelete.value, 'name')}".`)
        putFocusNextTick(nextFocusId)
        deleteModalBody.value = templateForDelete.value = undefined
        isBusy.value = isDeleting.value = false
      })
    })
  }
}

const edit = (template: DegreeTemplate) => {
  templateForEdit.value = clone(template)
  isBusy.value = true
  putFocusNextTick('rename-template-input')
}

const getNextFocusId = (currentTemplateId: number, action: string) => {
  const currentTemplateIndex = findIndex(props.degreeTemplates, {id: currentTemplateId})
  const lastTemplateIndex = size(props.degreeTemplates) - 1
  if (lastTemplateIndex > 0) {
    const nextTemplateIndex = (currentTemplateIndex === lastTemplateIndex ) ? currentTemplateIndex - 1 : currentTemplateIndex + 1
    const nextTemplateId = get(props.degreeTemplates, `${nextTemplateIndex}.id`)
    return `degree-check-${nextTemplateId}-${action}-btn`
  }
  return 'show-hide-archived-degree-templates'
}

const isNameAvailable = (name: string, ignoreTemplateId: number) => {
  const lower = name.trim().toLowerCase()
  const templates = ignoreTemplateId ? _filter(props.degreeTemplates, t => t.id !== ignoreTemplateId) : props.degreeTemplates
  return map(templates, 'name').findIndex(t => t.toLowerCase() === lower) === -1
}

const openCreateCloneModal = (template: DegreeTemplate) => {
  templateToClone.value = template
  isBusy.value = true
}

const save = () => {
  if (templateForEdit.value) {
    const name = trim(templateForEdit.value.name)
    if (name) {
      const templateId = templateForEdit.value.id
      isRenaming.value = true
      alertScreenReader('Renaming template')
      updateDegreeTemplate(templateForEdit.value.id, name).then(() => {
        props.onUpdateDegreeTemplate(templateForEdit.value).then(() => {
          templateForEdit.value = undefined
          isRenaming.value = false
          putFocusNextTick(`degree-check-${templateId}-rename-btn`)
          alertScreenReader(`Saved changes to template "${name}"`)
          isBusy.value = false
        })
      })
    }
  }
}

const showDeleteModal = template => {
  deleteModalBody.value = `Are you sure you want to delete <b>"${template.name}"</b>?`
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
  font-weight: 700 !important;
  height: 30px !important;
}
</style>

<style scoped>
.degree-check-btn {
  padding: 1px 2px;
}
</style>
