<template>
  <div class="pb-3" :class="{'pl-2 pt-2': !isCampusRequirement}">
    <div v-if="!isCampusRequirement">
      <label for="recommended-course-checkbox" class="font-size-14 font-weight-bold mb-1">Course Indicators</label>
      <div class="pl-1">
        <v-checkbox
          id="recommended-course-checkbox"
          v-model="isRecommended"
          color="primary"
          hide-details
          label="Recommended course"
        />
        <v-checkbox
          id="ignored-course-checkbox"
          v-model="isIgnored"
          color="primary"
          hide-details
          label="Completed or ignored requirement"
        />
      </div>
    </div>
    <div v-if="!isCampusRequirement" class="mt-2">
      <UnitsInput
        :disable="isSaving"
        :error-message="unitsErrorMessage"
        :on-escape="cancel"
        :on-submit="onSubmit"
        :range="true"
        :set-units-lower="units => unitsLower = units"
        :set-units-upper="units => unitsUpper = units"
        :units-lower="unitsLower"
        :units-upper="unitsUpper"
      />
    </div>
    <div v-if="!isCampusRequirement" class="mt-2">
      <label for="grade-input" class="font-weight-500 pr-2">
        Grade
      </label>
      <v-text-field
        id="grade-input"
        v-model="grade"
        class="grade-input mt-1"
        hide-details
        maxlength="3"
        @keydown.enter="onSubmit"
      />
    </div>
    <div v-if="!isCampusRequirement" class="mt-2">
      <AccentColorSelect
        :accent-color="accentColor"
        :on-change="value => accentColor = value"
      />
    </div>
    <div class="mt-2">
      <label for="recommendation-note-textarea" class="font-weight-500">Note</label>
      <v-textarea
        id="recommendation-note-textarea"
        v-model="note"
        density="compact"
        :disabled="isSaving"
        hide-details
        rows="3"
        variant="outlined"
        @keyup.esc="cancel"
      />
    </div>
    <div class="d-flex mt-2">
      <ProgressButton
        id="update-requirement-btn"
        :action="onSubmit"
        class="mr-1"
        color="primary"
        :disabled="disableSaveButton"
        :in-progress="isSaving"
        size="small"
        :text="isSaving ? 'Saving...' : 'Save'"
      />
      <v-btn
        id="cancel-edit-requirement-btn"
        color="primary"
        :disabled="isSaving"
        size="small"
        text="Cancel"
        variant="outlined"
        @click="cancel"
      />
    </div>
  </div>
</template>

<script setup>
import AccentColorSelect from '@/components/degree/student/AccentColorSelect'
import ProgressButton from '@/components/util/ProgressButton'
import UnitsInput from '@/components/degree/UnitsInput'
import {alertScreenReader} from '@/lib/utils'
import {
  isCampusRequirement as _isCampusRequirement,
  validateUnitRange
} from '@/lib/degree-progress'
import {putFocusNextTick} from '@/lib/utils'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {updateCourseRequirement} from '@/api/degree'
import {computed, onMounted, ref} from 'vue'
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
  category: {
    required: true,
    type: Object
  }
})

const degreeStore = useDegreeStore()

const accentColor = ref(props.category.accentColor)
const grade = ref(props.category.grade)
const isCampusRequirement = _isCampusRequirement(props.category)
const isIgnored = ref(props.category.isIgnored)
const isRecommended = ref(props.category.isRecommended)
const isSaving = ref(false)
const note = ref(props.category.note)
const unitsLower = ref(props.category.unitsLower)
const unitsUpper = ref(props.category.unitsUpper)

const disableSaveButton = computed(() => {
  return isSaving.value || !!unitsErrorMessage.value
})

const unitsErrorMessage = computed(() => {
  const validate = !!unitsLower.value || !!unitsUpper.value
  return validate ? validateUnitRange(unitsLower.value, unitsUpper.value, 10).message : null
})

onMounted(() => putFocusNextTick('recommended-course-checkbox'))

const cancel = () => {
  isIgnored.value = undefined
  isRecommended.value = undefined
  props.afterCancel()
}

const onSubmit = () => {
  if (!disableSaveButton.value) {
    isSaving.value = true
    const done = () => {
      alertScreenReader('Requirement updated')
      isSaving.value = false
      props.afterSave()
    }
    updateCourseRequirement(
      accentColor.value,
      props.category.id,
      grade.value,
      isIgnored.value,
      isRecommended.value,
      note.value,
      unitsLower.value,
      unitsUpper.value
    ).then(() => refreshDegreeTemplate(degreeStore.templateId)).then(done)
  }
}
</script>

<style scoped>
.grade-input {
  width: 3rem;
}
</style>
