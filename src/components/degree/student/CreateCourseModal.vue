<template>
  <div>
    <v-btn
      :id="`create-course-under-parent-category-${parentCategory.id}`"
      class="font-size-14 font-weight-bold pl-0"
      color="primary"
      :disabled="degreeStore.disableButtons"
      variant="text"
      v-bind="props"
      @click="openModal"
    >
      <div class="align-center d-flex justify-space-between">
        <div>
          <v-icon size="22" :icon="mdiPlus" />
        </div>
        <div>
          Manually Create Course
        </div>
      </div>
    </v-btn>
  </div>
  <v-dialog
    v-model="showModal"
    aria-labelledby="modal-header"
    persistent
    @update:model-value="onToggle"
  >
    <v-card class="modal-content" min-width="600">
      <FocusLock @keydown.esc="cancel">
        <v-card-title>
          <ModalHeader text="Create Course" />
        </v-card-title>
        <v-card-text class="modal-body">
          <div>
            <label
              for="course-name-input"
              class="font-weight-700 mb-1"
            >
              <span class="sr-only">Course </span>Name
            </label>
            <v-text-field
              id="course-name-input"
              v-model="name"
              class="cohort-create-input-name"
              density="comfortable"
              hide-details
              maxlength="255"
              variant="outlined"
            />
            <div class="text-grey mb-3"><span class="sr-only">Course name has a </span>255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></div>
            <div
              v-if="error"
              id="create-error"
              class="text-error"
              aria-live="polite"
              role="alert"
            >
              {{ error }}
            </div>
            <div
              v-if="name.length === 255"
              class="sr-only"
              aria-live="polite"
            >
              Course name cannot exceed 255 characters.
            </div>
          </div>
          <div class="pb-2">
            <UnitsInput
              :disable="isSaving"
              :error-message="unitsErrorMessage"
              input-id="course-units-input"
              label-class="font-weight-700 mb-1 pr-2"
              :on-submit="save"
              :set-units-lower="setUnits"
              :units-lower="units"
            />
          </div>
          <div class="pb-3">
            <label id="units-grade-label" for="course-grade-input" class="font-weight-700 mb-1 pr-2">
              Grade
            </label>
            <v-text-field
              id="course-grade-input"
              v-model="grade"
              :aria-autocomplete="false"
              aria-labelledby="units-grade-label"
              class="grade-input"
              density="compact"
              hide-details
              maxlength="3"
              variant="outlined"
              @keydown.enter="save"
            />
          </div>
          <div class="pb-3">
            <AccentColorSelect
              :accent-color="accentColor"
              :on-change="value => accentColor = value"
            />
          </div>
          <label for="course-note-textarea" class="font-weight-700">
            Note
          </label>
          <div class="pb-2">
            <v-textarea
              id="course-note-textarea"
              v-model="note"
              :disabled="isSaving"
              hide-details
              rows="4"
              variant="outlined"
            />
          </div>
        </v-card-text>
        <v-card-actions class="modal-footer">
          <ProgressButton
            id="create-course-save-btn"
            :action="save"
            color="primary"
            :disabled="disableSaveButton"
            :in-progress="isSaving"
            :text="isSaving ? 'Saving' : 'Save'"
          />
          <v-btn
            id="create-course-cancel-btn"
            class="ml-2"
            :disabled="isSaving"
            text="Cancel"
            variant="text"
            @click="cancel"
          />
        </v-card-actions>
      </FocusLock>
    </v-card>
  </v-dialog>
</template>

<script setup>
import AccentColorSelect from '@/components/degree/student/AccentColorSelect'
import FocusLock from 'vue-focus-lock'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import UnitsInput from '@/components/degree/UnitsInput'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {createCourse} from '@/api/degree'
import {mdiPlus} from '@mdi/js'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {validateUnitRange} from '@/lib/degree-progress'
import {computed, onUnmounted, ref} from 'vue'
import {isEmpty as _isEmpty, trim} from 'lodash'
import {useDegreeStore} from '@/stores/degree-edit-session/index'

const props = defineProps({
  parentCategory: {
    required: true,
    type: Object
  }
})

const degreeStore = useDegreeStore()

const accentColor = ref(undefined)
const error = ref(undefined)
const grade = ref(undefined)
const isSaving = ref(false)
const name = ref('')
const note = ref('')
const showModal = ref(false)
const units = ref(undefined)

const disableSaveButton = computed(() => {
  return isSaving.value || !!unitsErrorMessage.value || !trim(name.value)
})
const unitsErrorMessage = computed(() => {
  const isEmpty = _isEmpty(trim(units.value))
  return isEmpty ? null : validateUnitRange(units.value, undefined, 10).message
})

onUnmounted(() => {
  closeModal()
})

const cancel = () => {
  closeModal()
  alertScreenReader('Canceled')
  putFocusNextTick(`create-course-under-parent-category-${props.parentCategory.id}`)
}

const closeModal = () => {
  accentColor.value = undefined
  error.value = undefined
  grade.value = undefined
  isSaving.value = false
  name.value = ''
  note.value = ''
  showModal.value = false
  units.value = undefined
  degreeStore.setDisableButtons(false)
}

const onToggle = isOpen => {
  if (!isOpen) {
    closeModal()
    putFocusNextTick(`create-course-under-parent-category-${props.parentCategory.id}`)
  }
}

const openModal = () => {
  showModal.value = true
  degreeStore.setDisableButtons(true)
  alertScreenReader('Create course dialog opened')
  putFocusNextTick('course-name-input')
}

const save = () => {
  if (!degreeStore.disableSaveButton) {
    isSaving.value = true
    createCourse(
      accentColor.value,
      degreeStore.templateId,
      trim(grade.value),
      trim(name.value),
      trim(note.value),
      props.parentCategory.id,
      degreeStore.sid,
      null,
      units.value
    ).then(course => {
      refreshDegreeTemplate(degreeStore.templateId).then(() => {
        closeModal()
        alertScreenReader(`Course ${course.name} created`)
        putFocusNextTick(`assign-course-${course.id}-btn`)
      })
    })
  }
}

const setUnits = value => {
  units.value = value
}
</script>

<style scoped>
.grade-input {
  width: 3rem;
}
</style>
