<template>
  <div id="edit-unassigned-course" class="pb-2">
    <div v-if="course.manuallyCreatedBy">
      <label
        for="course-name-input"
        class="font-weight-bolder mb-1"
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
      <div class="faint-text mb-2"><span class="sr-only">Course name has a </span>255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></div>
      <div
        v-if="error"
        id="create-error"
        class="has-error"
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
        :on-submit="update"
        :set-units-lower="setUnits"
        :units-lower="units"
      />
    </div>
    <div v-if="course.manuallyCreatedBy" class="pb-2">
      <label id="units-grade-label" for="course-grade-input" class="font-weight-bolder mb-1 pr-2">
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
        @keypress.enter="update"
      />
    </div>
    <div v-if="course.manuallyCreatedBy" class="pb-2">
      <AccentColorSelect
        :accent-color="accentColor"
        :on-change="value => accentColor = value"
      />
    </div>
    <div v-if="course.categoryId || course.manuallyCreatedBy">
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
    <label for="course-note-textarea" class="font-weight-500 pb-0">
      Note
    </label>
    <div class="pb-3">
      <b-form-textarea
        id="course-note-textarea"
        v-model="note"
        :disabled="isSaving"
        rows="4"
      />
    </div>
    <div class="d-flex">
      <div class="pr-2">
        <b-btn
          id="update-note-btn"
          class="btn-primary-color-override px-3"
          :disabled="disableSaveButton"
          size="sm"
          variant="primary"
          @click="update"
        >
          <span v-if="isSaving">
            <font-awesome class="mr-1" icon="spinner" spin /> Saving
          </span>
          <span v-if="!isSaving">Save</span>
        </b-btn>
      </div>
      <div>
        <b-btn
          id="cancel-update-note-btn"
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
import SelectUnitFulfillment from '@/components/degree/SelectUnitFulfillment'
import UnitsInput from '@/components/degree/UnitsInput'
import Util from '@/mixins/Util'

export default {
  name: 'EditCourse',
  mixins: [DegreeEditSession, Util],
  components: {AccentColorSelect, SelectUnitFulfillment, UnitsInput},
  props: {
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
  },
  data: () => ({
    accentColor: undefined,
    error: undefined,
    grade: undefined,
    isSaving: false,
    name: undefined,
    note: '',
    selectedUnitRequirements: [],
    units: undefined
  }),
  computed: {
    disableSaveButton() {
      return !!(this.isSaving || this.unitsErrorMessage || (this.course.manuallyCreatedBy && !this.$_.trim(this.name)))
    },
    unitsErrorMessage() {
      const isEmpty = this.$_.isEmpty(this.$_.trim(this.units))
      if (isEmpty && this.course.manuallyCreatedBy) {
        return null
      }
      return isEmpty ? 'Required' : this.validateUnitRange(this.units, undefined, 10).message
    }
  },
  created() {
    this.accentColor = this.course.accentColor
    this.grade = this.course.grade
    this.name = this.course.name
    this.note = this.course.note
    this.units = this.course.units
    this.selectedUnitRequirements = this.$_.clone(this.course.unitRequirements)
    this.$putFocusNextTick(this.course.manuallyCreatedBy ? 'course-name-input' : 'course-units-input')
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled')
      this.afterCancel()
    },
    onUnitRequirementsChange(unitRequirements) {
      this.selectedUnitRequirements = unitRequirements
    },
    setUnits(units) {
      this.units = units
    },
    update() {
      if (!this.disableSaveButton) {
        this.isSaving = true
        this.updateCourse({
          accentColor: this.accentColor,
          courseId: this.course.id,
          grade: this.grade,
          name: this.name,
          note: this.note,
          unitRequirementIds: this.$_.map(this.selectedUnitRequirements, 'id'),
          units: this.units
        }).then(data => {
          this.$announcer.polite('Course updated')
          this.afterSave(data)
        })
      }
    }
  }
}
</script>

<style scoped>
.grade-input {
  width: 3rem;
}
</style>
