<template>
  <div class="pb-3 pl-2 pt-2">
    <div class="mb-2">
      <label for="recommended-course-checkbox" class="font-size-14 font-weight-bolder mb-1">Course Indicator</label>
      <b-form-checkbox
        id="recommended-course-checkbox"
        v-model="isRecommended"
      >
        Recommended course
      </b-form-checkbox>
    </div>
    <div class="pb-2">
      <UnitsInput
        :disable="isSaving"
        :error-message="unitsErrorMessage"
        :on-submit="onSubmit"
        :range="true"
        :set-units-lower="setUnitsLower"
        :set-units-upper="setUnitsUpper"
        :units-lower="unitsLower"
        :units-upper="unitsUpper"
      />
    </div>
    <div class="pb-2">
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
    <div class="pb-2">
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
            <font-awesome class="mr-1" icon="spinner" spin /> Saving
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
import DegreeEditSession from '@/mixins/DegreeEditSession'
import UnitsInput from '@/components/degree/UnitsInput'

export default {
  name: 'EditCourseRequirement',
  mixins: [DegreeEditSession],
  components: {AccentColorSelect, UnitsInput},
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
      return validate ? this.validateUnitRange(this.unitsLower, this.unitsUpper, 10).message : null
    }
  },
  created() {
    this.accentColor = this.category.accentColor
    this.grade = this.category.grade
    this.isRecommended = this.category.isRecommended
    this.note = this.category.note
    this.unitsLower = this.category.unitsLower
    this.unitsUpper = this.category.unitsUpper
    this.$putFocusNextTick('recommended-course-checkbox')
  },
  methods: {
    cancel() {
      this.isRecommended = undefined
      this.afterCancel()
    },
    onSubmit() {
      if (!this.disableSaveButton) {
        this.isSaving = true
        const done = () => {
          this.$announcer.polite('Requirement updated')
          this.isSaving = false
          this.afterSave()
        }
        this.updateCourseRequirement({
          accentColor: this.accentColor,
          categoryId: this.category.id,
          grade: this.grade,
          isRecommended: this.isRecommended,
          note: this.note,
          unitsLower: this.unitsLower,
          unitsUpper: this.unitsUpper
        }).then(done)
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
