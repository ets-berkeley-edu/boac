<template>
  <div id="edit-unassigned-course" class="pb-2">
    <div v-if="course.manuallyCreatedBy">
      <label
        for="course-name-input"
        class="font-weight-bold mb-1"
      >
        <span class="sr-only">Course </span>Name
      </label>
      <v-text-field
        id="course-name-input"
        v-model="name"
        density="comfortable"
        :disabled="isSaving"
        hide-details
        maxlength="255"
      />
      <div class="text-surface-variant mb-2"><span class="sr-only">Course name has a </span>255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></div>
      <div
        v-if="error"
        id="create-error"
        aria-live="polite"
        class="text-error"
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
    <div v-if="course.manuallyCreatedBy" class="mt-2">
      <label for="course-grade-input" class="font-weight-bold">
        Grade
      </label>
      <v-text-field
        id="course-grade-input"
        v-model="grade"
        aria-label="Course Grade"
        class="grade-input"
        :disabled="isSaving"
        hide-details
        maxlength="3"
        @keydown.enter="update"
      />
    </div>
    <div>
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
    <div v-if="course.manuallyCreatedBy" class="mt-2">
      <AccentColorSelect
        :accent-color="accentColor"
        :disabled="isSaving"
        :on-change="value => accentColor = value"
      />
    </div>
    <div class="mt-2">
      <label for="course-note-textarea" class="font-weight-500">
        <span class="sr-only">Course</span>Note
      </label>
      <v-textarea
        id="course-note-textarea"
        v-model="note"
        density="compact"
        :disabled="isSaving"
        hide-details
        rows="3"
        variant="outlined"
        @keyup.esc="cancel"
      />
    </div>
    <div class="align-center d-flex justify-end mt-2">
      <ProgressButton
        id="update-note-btn"
        :action="update"
        aria-label="Save Course"
        class="mr-1"
        color="primary"
        :disabled="disableSaveButton"
        :in-progress="isSaving"
        size="small"
        :text="isSaving ? 'Saving...' : 'Save'"
      />
      <div>
        <v-btn
          id="cancel-update-note-btn"
          aria-label="Cancel Edit Course"
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
import {isEmpty, map, size, trim} from 'lodash'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import ProgressButton from '@/components/util/ProgressButton.vue'

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

const accentColor = ref(props.course.accentColor)
const error = ref(undefined)
const grade = ref(props.course.grade)
const isSaving = ref(false)
const name = ref(props.course.name)
const note = ref(props.course.note)
const selectedUnitRequirements = ref(props.course.unitRequirements)
const units = ref(props.course.units)

const disableSaveButton = computed(() => {
  return !!(isSaving.value || unitsErrorMessage.value || (props.course.manuallyCreatedBy && !trim(name.value)))
})

const unitsErrorMessage = computed(() => {
  const isEmptyUnits = isEmpty(trim(units.value))
  if (isEmptyUnits && props.course.manuallyCreatedBy) {
    return null
  }
  return isEmptyUnits ? 'Required' : validateUnitRange(units.value, undefined, 10).message
})

onMounted(() => {
  putFocusNextTick(props.course.manuallyCreatedBy ? 'course-name-input' : `column-${props.position}-unit-requirement-select`)
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
    alertScreenReader('Saving')
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
