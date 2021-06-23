<template>
  <div id="edit-unassigned-course" class="pb-3">
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
    <div v-if="course.categoryId">
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
    <label for="course-note-textarea" class="font-weight-500 pb-1">
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
import DegreeEditSession from '@/mixins/DegreeEditSession'
import SelectUnitFulfillment from '@/components/degree/SelectUnitFulfillment'
import UnitsInput from '@/components/degree/UnitsInput'
import Util from '@/mixins/Util'

export default {
  name: 'EditCourse',
  mixins: [DegreeEditSession, Util],
  components: {SelectUnitFulfillment, UnitsInput},
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
    isSaving: false,
    note: '',
    selectedUnitRequirements: [],
    units: undefined
  }),
  computed: {
    disableSaveButton() {
      return this.isSaving || !!this.unitsErrorMessage
    },
    unitsErrorMessage() {
      const isEmpty = this.$_.isEmpty(this.$_.trim(this.units))
      return isEmpty ? 'Required' : this.validateUnitRange(this.units, undefined, 10).message
    }
  },
  created() {
    this.note = this.course.note
    this.units = this.course.units
    this.selectedUnitRequirements = this.$_.clone(this.course.unitRequirements)
    this.$putFocusNextTick('course-units-input')
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
          courseId: this.course.id,
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
