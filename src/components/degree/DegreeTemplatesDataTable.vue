<template>
  <div>
    <div v-if="!degreeTemplates.length">
      There are no {{ mode === 'archived' ? 'archived degree templates.' : 'degree templates available.' }}
    </div>
    <div v-if="degreeTemplates.length" class="pt-2 w-100">
      <v-data-table
        id="degree-checks-table"
        v-table-caption="tableCaption"
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
              :aria-describedby="`${errorMessage ? 'rename-template-input-error' : ''} rename-template-counter`"
              :aria-invalid="!templateForEdit.name"
              aria-required="true"
              autocomplete="on"
              class="bg-white w-100"
              :disabled="isRenaming"
              :error="!!errorMessage"
              :error-messages="errorMessage"
              label="Degree Name"
              :maxlength="255"
              persistent-counter
              required
              :rules="[validate]"
              validate-on="lazy submit"
              @keydown.enter="save"
              @keyup.esc="cancelEdit"
              @update:model-value="resetValidation"
            >
              <template #counter="{max, value}">
                <CharacterCount
                  v-if="max"
                  :count="toInt(value || 0)"
                  id-prefix="rename-template"
                  :max="toInt(max)"
                />
              </template>
              <template #message="{message}">
                <v-alert
                  id="rename-template-input-error"
                  class="font-size-14 line-height-normal"
                  density="compact"
                  role="none"
                  type="error"
                  variant="tonal"
                >
                  <span v-html="message" />
                </v-alert>
              </template>
            </v-text-field>
          </div>
          <div v-if="item.id !== get(templateForEdit, 'id')">
            <component
              :is="isBusy ? 'span' : 'router-link'"
              :id="`degree-check-${item.id}-link`"
              :aria-disabled="isBusy"
              class="d-inline-block"
              :class="{'text-disabled': isBusy}"
              role="link"
              :to="`/degree/${item.id}`"
              v-html="`${item.name}`"
            />
          </div>
        </template>
        <template #item.createdAt="{item}">
          <div
            v-if="item.createdAt"
            class="text-no-wrap"
            :class="{
              'text-disabled': isBusy && item.id !== get(templateForEdit, 'id'),
              'h-100 pt-6': templateForEdit && item.id === templateForEdit.id
            }"
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
              :disabled="isRenaming"
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
              <span :aria-hidden="true" class="text-disabled">|</span>
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
            <div v-if="currentUser.canEditDegreeProgress" class="d-flex flex-wrap flex-sm-nowrap justify-end pb-1">
              <div class="align-center d-flex">
                <span :aria-hidden="true" class="text-disabled">|</span>
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
                <span :aria-hidden="true" class="text-disabled">|</span>
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
                <span :aria-hidden="true" class="text-disabled">|</span>
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
      :after-create="afterClone"
      :cancel="cloneCanceled"
      :existing-templates="degreeTemplates"
      :show-modal="!!templateToClone"
      :template-to-clone="templateToClone"
    />
  </div>
</template>

<script lang="ts" setup>
import type {PropType} from 'vue'
import {clone, findIndex, get, reject, size, trim} from 'lodash'
import {computed, ref} from 'vue'
import {DateTime} from 'luxon'
import type {DegreeTemplate} from '@/lib/types'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import CharacterCount from '@/components/util/CharacterCount.vue'
import CloneTemplateModal from '@/components/degree/CloneTemplateModal.vue'
import ProgressButton from '@/components/util/ProgressButton.vue'
import {alertScreenReader, putFocusNextTick, toInt} from '@/lib/utils'
import {
  archiveDegreeTemplate,
  deleteDegreeTemplate,
  unarchiveDegreeTemplate,
  updateDegreeTemplate,
} from '@/api/degree'
import {useContextStore} from '@/stores/context'
import {validateDegreeTemplateName} from '@/lib/degree-progress'

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
const errorMessage = ref<string | undefined>()
const isBusy = ref(false)
const isDeleting = ref(false)
const isRenaming = ref(false)
const templateForDelete = ref<DegreeTemplate | undefined>()
const templateForEdit = ref<DegreeTemplate | undefined>()
const templateToClone = ref<DegreeTemplate | undefined>()

const tableCaption = computed(() =>
  props.mode === 'archived' ? 'Archived degree checks' : 'Degree checks'
)

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
    resetValidation()
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
  errorMessage.value = ''
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

const openCreateCloneModal = (template: DegreeTemplate) => {
  templateToClone.value = template
  isBusy.value = true
}

const resetValidation = () => {
  errorMessage.value = ''
}

const save = () => {
  if (templateForEdit.value) {
    isRenaming.value = true
    if (validate() === true) {
      const name = trim(templateForEdit.value.name)
      const templateId = templateForEdit.value.id
      alertScreenReader('Renaming template')
      updateDegreeTemplate(templateId, name).then(() => {
        props.onUpdateDegreeTemplate(templateForEdit.value).then(() => {
          templateForEdit.value = undefined
          putFocusNextTick(`degree-check-${templateId}-rename-btn`)
          alertScreenReader(`Saved changes to template "${name}"`)
          isBusy.value = isRenaming.value = false
        })
      })
    } else {
      putFocusNextTick('rename-template-input')
      isRenaming.value = false
    }
  }
}

const showDeleteModal = (template: DegreeTemplate) => {
  deleteModalBody.value = `Are you sure you want to delete <b>"${template.name}"</b>?`
  templateForDelete.value = template
  isBusy.value = isDeleting.value = true
}

const validate = () => {
  const validationReport = validateDegreeTemplateName(
    trim(get(templateForEdit.value, 'name')),
    reject(props.degreeTemplates, {'id': get(templateForEdit.value, 'id')})
  )
  errorMessage.value = validationReport.message
  return validationReport.valid || validationReport.message
}
</script>

<style>
#degree-checks-table table {
  border-collapse: collapse;
  table-layout: fixed;
  width: 100%;
}
.bg-surface-light {
  .v-input__details {
    background-color: rgba(var(--v-theme-surface-light));
  }
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
