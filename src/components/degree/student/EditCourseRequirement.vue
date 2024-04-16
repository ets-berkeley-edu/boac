<template>
  <div class="pb-3 pl-2 pt-2">
    <div v-if="!isCampusRequirement(category)" class="mb-2">
      <label for="recommended-course-checkbox" class="font-size-14 font-weight-700 mb-1">Course Indicators</label>
      <div class="pl-1">
        <b-form-checkbox
          id="recommended-course-checkbox"
          v-model="isRecommended"
        >
          Recommended course
        </b-form-checkbox>
        <b-form-checkbox
          id="ignored-course-checkbox"
          v-model="isIgnored"
        >
          Completed or ignored requirement
        </b-form-checkbox>
      </div>
    </div>
    <div v-if="!isCampusRequirement(category)" class="pb-2">
      <UnitsInput
        :disable="isSaving"
        :error-message="unitsErrorMessage"
        :on-escape="cancel"
        :on-submit="onSubmit"
        :range="true"
        :set-units-lower="setUnitsLower"
        :set-units-upper="setUnitsUpper"
        :units-lower="unitsLower"
        :units-upper="unitsUpper"
      />
    </div>
    <div v-if="!isCampusRequirement(category)" class="pb-2">
      <label id="grade-label" for="grade-input" class="font-weight-500 mb-1 pr-2">
        Grade
      </label>
      <b-form-input
        id="grade-input"
        v-model="grade"
        aria-labelledby="grade-label"
        class="grade-input"
        maxlength="3"
        size="sm"
        trim
        @keypress.enter="onSubmit"
      />
    </div>
    <div v-if="!isCampusRequirement(category)" class="pb-2">
      <AccentColorSelect
        :accent-color="accentColor"
        :on-change="value => accentColor = value"
      />
    </div>
    <div>
      <label for="recommendation-note-textarea" class="font-weight-500 pb-0">Note</label>
      <div class="pb-3">
        <b-form-textarea
          id="recommendation-note-textarea"
          v-model="note"
          :disabled="isSaving"
          rows="4"
          @keyup.esc="cancel"
        />
      </div>
    </div>
    <div class="d-flex">
      <div class="pr-2">
        <b-btn
          id="update-requirement-btn"
          class="btn-primary-color-override"
          :disabled="disableSaveButton"
          size="sm"
          variant="primary"
          @click="onSubmit"
        >
          <span v-if="isSaving">
            <v-progress-circular class="mr-1" size="small" />
          </span>
          <span v-if="!isSaving">Save</span>
        </b-btn>
      </div>
      <div>
        <b-btn
          id="cancel-edit-requirement-btn"
          class="btn-primary-color-override btn-primary-color-outline-override"
          :disabled="isSaving"
          size="sm"
          variant="outline-primary"
          @click="cancel"
        >
          Cancel
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import AccentColorSelect from '@/components/degree/student/AccentColorSelect'
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import UnitsInput from '@/components/degree/UnitsInput'
import {isCampusRequirement, validateUnitRange} from '@/lib/degree-progress'
import {putFocusNextTick} from '@/lib/utils'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {updateCourseRequirement} from '@/api/degree'

export default {
  name: 'EditCourseRequirement',
  components: {AccentColorSelect, UnitsInput},
  mixins: [Context, DegreeEditSession],
  props: {
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
  },
  data: () => ({
    accentColor: undefined,
    grade: undefined,
    isIgnored: undefined,
    isRecommended: undefined,
    isSaving: false,
    note: undefined,
    unitsLower: undefined,
    unitsUpper: undefined
  }),
  computed: {
    disableSaveButton() {
      return this.isSaving || !!this.unitsErrorMessage
    },
    unitsErrorMessage() {
      const validate = !!this.unitsLower || !!this.unitsUpper
      return validate ? validateUnitRange(this.unitsLower, this.unitsUpper, 10).message : null
    }
  },
  created() {
    this.accentColor = this.category.accentColor
    this.grade = this.category.grade
    this.isIgnored = this.category.isIgnored
    this.isRecommended = this.category.isRecommended
    this.note = this.category.note
    this.unitsLower = this.category.unitsLower
    this.unitsUpper = this.category.unitsUpper
    putFocusNextTick('recommended-course-checkbox')
  },
  methods: {
    cancel() {
      this.isIgnored = undefined
      this.isRecommended = undefined
      this.afterCancel()
    },
    isCampusRequirement,
    onSubmit() {
      if (!this.disableSaveButton) {
        this.isSaving = true
        const done = () => {
          this.alertScreenReader('Requirement updated')
          this.isSaving = false
          this.afterSave()
        }
        updateCourseRequirement(
          this.accentColor,
          this.category.id,
          this.grade,
          this.isIgnored,
          this.isRecommended,
          this.note,
          this.unitsLower,
          this.unitsUpper
        ).then(() => refreshDegreeTemplate(this.templateId)).then(done)
      }
    },
    setUnitsLower(units) {
      this.unitsLower = units
    },
    setUnitsUpper(units) {
      this.unitsUpper = units
    }
  }
}
</script>

<style scoped>
.grade-input {
  width: 3rem;
}
</style>
