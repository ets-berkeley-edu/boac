<template>
  <div>
    <div class="font-size-14">
      <v-btn
        :id="`create-course-under-parent-category-${parentCategory.id}`"
        class="font-weight-500 p-0"
        :disabled="disableButtons"
        variant="text"
        @click.prevent="openModal"
      >
        <v-icon class="font-size-16" :icon="mdiPlus" /> Manually Create Course
      </v-btn>
    </div>
    <b-modal
      v-model="showModal"
      body-class="pl-0 pr-0"
      hide-footer
      hide-header
      @shown="putFocusNextTick('modal-header')"
      @hidden="closeModal"
    >
      <div>
        <ModalHeader text="Create Course" />
        <div class="modal-body">
          <div>
            <label
              for="course-name-input"
              class="font-weight-700 mb-1"
            >
              <span class="sr-only">Course </span>Name
            </label>
            <b-form-input
              id="course-name-input"
              v-model="name"
              class="cohort-create-input-name"
              maxlength="255"
              size="md"
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
            <b-form-input
              id="course-grade-input"
              v-model="grade"
              aria-labelledby="units-grade-label"
              class="grade-input"
              maxlength="3"
              size="sm"
              trim
              @keypress.enter="save"
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
            <b-form-textarea
              id="course-note-textarea"
              v-model="note"
              :disabled="isSaving"
              rows="4"
            />
          </div>
        </div>
        <div class="modal-footer pb-0">
          <form @submit.prevent="_noop">
            <b-btn
              id="create-course-save-btn"
              class="btn-primary-color-override"
              :disabled="disableSaveButton"
              variant="primary"
              @click.prevent="save"
            >
              Save
            </b-btn>
            <b-btn
              id="create-course-cancel-btn"
              class="pl-2"
              variant="link"
              @click="cancel"
            >
              Cancel
            </b-btn>
          </form>
        </div>
      </div>
    </b-modal>
  </div>
</template>

<script setup>
import AccentColorSelect from '@/components/degree/student/AccentColorSelect'
import ModalHeader from '@/components/util/ModalHeader'
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
  return isEmpty ? null : validateUnitRange(this.units, undefined, 10).message
})

onUnmounted(() => {
  closeModal()
})

const cancel = () => {
  closeModal()
  alertScreenReader('Canceled')
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

const openModal = () => {
  showModal.value = true
  degreeStore.setDisableButtons(true)
  alertScreenReader('Create course dialog opened')
}

const save = () => {
  if (!degreeStore.disableSaveButton) {
    isSaving.value = true
    createCourse(
      this.accentColor.value,
      degreeStore.templateId,
      trim(grade.value),
      trim(name.value),
      trim(note.value),
      props.parentCategory.id,
      degreeStore.sid,
      units.value
    ).then(course => {
      refreshDegreeTemplate(degreeStore.templateId).then(() => {
        closeModal()
        alertScreenReader(`Course ${course.name} created`)
        putFocusNextTick(`assign-course-${course.id}-dropdown`, 'button')
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
