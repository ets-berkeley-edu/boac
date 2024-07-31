<template>
  <div id="edit-unassigned-course" class="pb-2">
    <div v-if="course.manuallyCreatedBy">
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
        maxlength="255"
        size="md"
      />
      <div class="text-grey mb-2"><span class="sr-only">Course name has a </span>255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></div>
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
    <div v-if="course.categoryId || size(selectedUnitRequirements)">
      <label :for="`column-${position}-unit-requirement-select`" class="font-weight-500">
        Counts Towards Unit Fulfillment
      </label>
      <div class="pb-2">
        <SelectUnitFulfillment
          :disable="isSaving"
          :initial-unit-requirements="selectedUnitRequirements"
          :on-unit-requirements-change="onUnitRequirementsChange"
          :position="position"
        />
      </div>
    </div>
    <div class="pb-2">
      <UnitsInput
        :disable="isSaving"
        :error-message="unitsErrorMessage"
        input-id="course-units-input"
        :on-escape="cancel"
        :on-submit="update"
        :set-units-lower="setUnits"
        :units-lower="units"
      />
    </div>
    <div v-if="course.manuallyCreatedBy" class="pb-2">
      <label id="grade-label" for="course-grade-input" class="font-weight-700 mb-1 pr-2">
        Grade
      </label>
      <v-text-field
        id="course-grade-input"
        v-model="grade"
        aria-labelledby="grade-label"
        class="grade-input"
        maxlength="3"
        size="sm"
        @keydown.enter="update"
      />
    </div>
    <div v-if="course.manuallyCreatedBy" class="pb-2">
      <AccentColorSelect
        :accent-color="accentColor"
        :on-change="value => accentColor = value"
      />
    </div>
    <label for="course-note-textarea" class="font-weight-500 pb-0">
      Note
    </label>
    <div class="pb-3">
      <v-textarea
        id="course-note-textarea"
        v-model="note"
        :disabled="isSaving"
        rows="4"
        variant="outlined"
        @keyup.esc="cancel"
      />
    </div>
    <div class="d-flex">
      <div class="pr-2">
        <v-btn
          id="update-note-btn"
          class="px-3"
          color="primary"
          :disabled="disableSaveButton"
          size="small"
          @click="update"
        >
          <span v-if="isSaving">
            <v-progress-circular class="mr-1" size="small" />
          </span>
          <span v-if="!isSaving">Save</span>
        </v-btn>
      </div>
      <div>
        <v-btn
          id="cancel-update-note-btn"
          color="primary"
          :disabled="isSaving"
          size="small"
          text="Cancel"
          variant="outlined"
          @click="cancel"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import AccentColorSelect from '@/components/degree/student/AccentColorSelect'
import SelectUnitFulfillment from '@/components/degree/SelectUnitFulfillment'
import UnitsInput from '@/components/degree/UnitsInput'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {updateCourse} from '@/api/degree'
import {validateUnitRange} from '@/lib/degree-progress'
import {computed, onMounted, ref} from 'vue'
import {clone, isEmpty as _isEmpty, map, size, trim} from 'lodash'
import {useDegreeStore} from '@/stores/degree-edit-session/index'

const props = defineProps({
  afterCancel: {
    required: true,
    type: Function
  },
  afterSave: {
    required: true,
    type: Function
  },
  course: {
    required: true,
    type: Object
  },
  position: {
    required: true,
    type: Number
  }
})

const degreeStore = useDegreeStore()

const accentColor = props.course.accentColor
const error = ref(undefined)
const grade = props.course.grade
const isSaving = ref(false)
const name = props.course.name
const note = props.course.note
const selectedUnitRequirements = clone(props.course.unitRequirements)
const units = props.course.units

const disableSaveButton = computed(() => {
  return !!(isSaving.value || unitsErrorMessage.value || (props.course.manuallyCreatedBy && !trim(name.value)))
})

const unitsErrorMessage = computed(() => {
  const isEmpty = _isEmpty(trim(units.value))
  if (isEmpty && props.course.manuallyCreatedBy) {
    return null
  }
  return isEmpty ? 'Required' : validateUnitRange(units.value, undefined, 10).message
})

onMounted(() => {
  putFocusNextTick(props.course.manuallyCreatedBy ? 'course-name-input' : 'course-units-input')
})

const cancel = () => {
  alertScreenReader('Canceled')
  props.afterCancel()
}

const onUnitRequirementsChange = unitRequirements => {
  selectedUnitRequirements.value = unitRequirements
}

const setUnits = value => {
  units.value = value
}

const update = () => {
  if (!disableSaveButton.value) {
    isSaving.value = true
    updateCourse(
      accentColor.value,
      props.course.id,
      grade.value,
      name.value,
      note.value,
      map(selectedUnitRequirements.value, 'id'),
      units.value
    ).then(data => {
      refreshDegreeTemplate(degreeStore.templateId).then(() => {
        alertScreenReader('Course updated')
        props.afterSave(data)
      })
    })
  }
}
</script>

<style scoped>
.grade-input {
  width: 3rem;
}
</style>
