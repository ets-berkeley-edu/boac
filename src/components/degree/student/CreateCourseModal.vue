<template>
  <div>
    <v-btn
      :id="`create-course-under-parent-category-${parentCategory.id}`"
      :aria-label="`Manually Create Course for ${parentCategory.name}`"
      class="font-weight-bold px-1 mt-1"
      color="primary"
      density="comfortable"
      :disabled="degreeStore.disableButtons"
      :prepend-icon="mdiPlus"
      text="Manually Create Course"
      variant="text"
      v-bind="props"
      @click="openModal"
    />
    <v-dialog
      v-model="showModal"
      aria-labelledby="modal-header"
      persistent
      @update:model-value="onToggle"
    >
      <v-card
        class="modal-content"
        :max-width="smAndDown ? 440 : undefined"
        :min-width="mdAndUp ? 600 : undefined"
      >
        <FocusLock :disabled="isFocusLockDisabled" @keydown.esc="() => cancel(false)">
          <v-card-title class="py-0 text-wrap">
            <ModalHeader :text="`Create Course for ${parentCategory.name}`" />
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
                autocomplete="on"
                class="mt-1"
                :disabled="isSaving"
                density="comfortable"
                maxlength="255"
                persistent-counter
                required
              >
                <template #counter="{max, value}">
                  <CharacterCount :count="toInt(value)" id-prefix="course-name" :max="toInt(max)" />
                </template>
              </v-text-field>
            </div>
            <div class="mt-2">
              <label id="units-grade-label" for="course-grade-input" class="font-weight-bold mb-1 pr-2">
                <span class="sr-only">Course </span>Grade
              </label>
              <v-text-field
                id="course-grade-input"
                v-model="grade"
                :aria-autocomplete="false"
                aria-labelledby="units-grade-label"
                class="grade-input mt-1"
                density="compact"
                :disabled="isSaving"
                hide-details
                maxlength="3"
                autocomplete="on"
                @keydown.enter="save"
              />
            </div>
            <div class="mt-2">
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
              <AccentColorSelect
                :accent-color="accentColor"
                :disabled="isSaving"
                :on-change="value => accentColor = value"
                :on-open-menu="isOpen => isFocusLockDisabled = isOpen"
              />
            </div>
            <div class="mt-3">
              <label for="course-note-textarea" class="font-weight-bold">
                <span class="sr-only">Course </span>Note
              </label>
              <div class="mt-1">
                <v-textarea
                  id="course-note-textarea"
                  v-model="note"
                  density="compact"
                  :disabled="isSaving"
                  hide-details
                  rows="4"
                  autocomplete="on"
                  variant="outlined"
                />
              </div>
            </div>
          </v-card-text>
          <v-card-actions class="modal-footer">
            <ProgressButton
              id="create-course-save-btn"
              :action="save"
              aria-label="Save Course"
              class="mr-1"
              color="primary"
              :disabled="disableSaveButton"
              :in-progress="isSaving"
              :text="isSaving ? 'Saving' : 'Save'"
            />
            <v-btn
              id="create-course-cancel-btn"
              aria-label="Cancel Create Course"
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
  </div>
</template>

<script setup>
import FocusLock from 'vue-focus-lock'
import {computed, nextTick, onUnmounted, ref, watch} from 'vue'
import {isEmpty as _isEmpty, trim} from 'lodash'
import {mdiPlus} from '@mdi/js'
import {useDisplay} from 'vuetify'
import AccentColorSelect from '@/components/degree/student/AccentColorSelect.vue'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import CharacterCount from '@/components/util/CharacterCount.vue'
import ModalHeader from '@/components/util/ModalHeader.vue'
import ProgressButton from '@/components/util/ProgressButton.vue'
import UnitsInput from '@/components/degree/UnitsInput.vue'
import {alertScreenReader, putFocusNextTick, toInt} from '@/lib/utils'
import {createCourse} from '@/api/degree'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/degree-edit-session-utils'
import {useDegreeStore} from '@/stores/degree-edit-session'
import {validateUnitRange} from '@/lib/degree-progress'

const props = defineProps({
  parentCategory: {
    required: true,
    type: Object
  }
})

const degreeStore = useDegreeStore()

const accentColor = ref(undefined)
const disableSaveButton = computed(() => isSaving.value || !!unitsErrorMessage.value || !trim(name.value))
const grade = ref(undefined)
const isDirty = computed(() => !!(accentColor.value || grade.value || name.value || trim(note.value) || units.value))
const isFocusLockDisabled = ref(false)
const isSaving = ref(false)
const name = ref('')
const note = ref('')
const showCancelConfirm = ref(false)
const showModal = ref(false)
const units = ref(undefined)
const unitsErrorMessage = computed(() => {
  const isEmpty = _isEmpty(trim(units.value))
  return isEmpty ? null : validateUnitRange(units.value, undefined, 10).message
})
const {mdAndUp, smAndDown} = useDisplay()

onUnmounted(() => {
  closeModal()
})

watch(showCancelConfirm, isShowing => nextTick(() => isFocusLockDisabled.value = isShowing))

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
  putFocusNextTick('course-name-input')
}

const save = () => {
  if (!disableSaveButton.value) {
    isSaving.value = true
    alertScreenReader('Saving')
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
        alertScreenReader(`${course.name} created`)
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
  width: 4rem;
}
</style>
