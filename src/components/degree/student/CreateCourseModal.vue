<template>
  <div>
    <v-btn
      :id="`create-course-under-parent-category-${parentCategory.id}`"
      class="font-weight-bold px-1"
      color="primary"
      density="comfortable"
      :disabled="degreeStore.disableButtons"
      :prepend-icon="mdiPlus"
      text="Manually Create Course"
      variant="text"
      v-bind="props"
      @click="openModal"
    />
  </div>
  <v-dialog
    v-model="showModal"
    aria-labelledby="modal-header"
    persistent
    @update:model-value="onToggle"
  >
    <v-card class="modal-content" min-width="600">
      <FocusLock @keydown.esc="() => cancel(false)">
        <v-card-title class="py-0">
          <ModalHeader text="Create Course" />
        </v-card-title>
        <v-card-text class="modal-body">
          <div>
            <label
              for="course-name-input"
              class="font-weight-bold"
            >
              <span class="sr-only">Course </span>Name
            </label>
            <v-text-field
              id="course-name-input"
              v-model="name"
              class="cohort-create-input-name mt-1"
              density="comfortable"
              hide-details
              maxlength="255"
            />
            <div class="text-surface-variant mb-3"><span class="sr-only">Course name has a </span>255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></div>
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
              aria-live="polite"
              class="sr-only"
              role="alert"
            >
              Course name cannot exceed 255 characters.
            </div>
          </div>
          <div class="mt-1">
            <UnitsInput
              :disable="isSaving"
              :error-message="unitsErrorMessage"
              input-id="course-units-input"
              label-class="font-weight-bold mb-1 pr-2"
              :on-submit="save"
              :set-units-lower="setUnits"
              :units-lower="units"
            />
          </div>
          <div class="mt-2">
            <label id="units-grade-label" for="course-grade-input" class="font-weight-bold mb-1 pr-2">
              Grade
            </label>
            <v-text-field
              id="course-grade-input"
              v-model="grade"
              :aria-autocomplete="false"
              aria-labelledby="units-grade-label"
              class="grade-input mt-1"
              hide-details
              maxlength="3"
              @keydown.enter="save"
            />
          </div>
          <div class="mt-2">
            <AccentColorSelect
              :accent-color="accentColor"
              :on-change="value => accentColor = value"
            />
          </div>
          <div class="mt-3">
            <label for="course-note-textarea" class="font-weight-bold">
              Note
            </label>
            <div class="mt-1">
              <v-textarea
                id="course-note-textarea"
                v-model="note"
                density="compact"
                :disabled="isSaving"
                hide-details
                rows="4"
                variant="outlined"
              />
            </div>
          </div>
        </v-card-text>
        <v-card-actions class="modal-footer">
          <ProgressButton
            id="create-course-save-btn"
            :action="save"
            class="mr-1"
            color="primary"
            :disabled="disableSaveButton"
            :in-progress="isSaving"
            :text="isSaving ? 'Saving' : 'Save'"
          />
          <v-btn
            id="create-course-cancel-btn"
            :disabled="isSaving"
            text="Cancel"
            variant="text"
            @click="() => cancel(false)"
          />
        </v-card-actions>
      </FocusLock>
    </v-card>
  </v-dialog>
  <AreYouSureModal
    v-model="showCancelConfirm"
    :function-confirm="() => cancel(true)"
    :function-cancel="() => showCancelConfirm = false"
    modal-header="Discard unsaved course?"
  />
</template>

<script setup>
import AccentColorSelect from '@/components/degree/student/AccentColorSelect'
import AreYouSureModal from '@/components/util/AreYouSureModal'
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
const showCancelConfirm = ref(false)
const units = ref(undefined)

const disableSaveButton = computed(() => isSaving.value || !!unitsErrorMessage.value || !trim(name.value))
const isDirty = computed(() => !!(accentColor.value || grade.value || name.value || trim(note.value) || units.value))
const unitsErrorMessage = computed(() => {
  const isEmpty = _isEmpty(trim(units.value))
  return isEmpty ? null : validateUnitRange(units.value, undefined, 10).message
})

onUnmounted(() => {
  closeModal()
})

const cancel = force => {
  if (!force && isDirty.value) {
    showCancelConfirm.value = true
  } else {
    closeModal()
    showCancelConfirm.value = false
    alertScreenReader('Canceled')
    putFocusNextTick(`create-course-under-parent-category-${props.parentCategory.id}`)
  }
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
