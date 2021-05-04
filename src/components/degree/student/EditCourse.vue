<template>
  <div id="edit-unassigned-course" class="pb-3">
    <div>
      <div class="font-weight-500 mb-1 mt-2">
        Units
      </div>
      <div class="units-input">
        <b-form-input
          id="course-units-input"
          v-model="units"
          :disabled="isSaving"
          maxlength="3"
          trim
          @keypress.enter="update"
        />
      </div>
      <div v-if="unitRequirements.length" class="mb-1 mt-2">
        <div class="font-weight-500">
          Counts Towards Unit Fulfillment
        </div>
        <div class="mb-3">
          <SelectUnitFulfillment
            :disable="isSaving"
            :initial-unit-requirements="selectedUnitRequirements"
            :on-unit-requirements-change="onUnitRequirementsChange"
            :position="position"
          />
        </div>
      </div>
      <div class="font-weight-500 mb-1 mt-2">
        Note
      </div>
      <div>
        <b-form-textarea
          id="course-note-textarea"
          v-model="note"
          :disabled="isSaving"
          rows="4"
        />
      </div>
    </div>
    <div class="d-flex mt-2">
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
import Util from '@/mixins/Util'

export default {
  name: 'EditCourse',
  mixins: [DegreeEditSession, Util],
  components: {SelectUnitFulfillment},
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
      return this.isSaving || !this.$_.trim(this.units)
    }
  },
  created() {
    this.note = this.course.note
    this.units = this.course.units
    this.putFocusNextTick('note-of-unassigned-course-textarea')
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled')
      this.afterCancel()
    },
    onUnitRequirementsChange(unitRequirements) {
      this.selectedUnitRequirements = unitRequirements
    },
    update() {
      if (!this.disableSaveButton) {
        this.isSaving = true
        this.updateCourse({
          courseId: this.course.id,
          note: this.note,
          unitRequirements: this.selectedUnitRequirements,
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
.units-input {
  max-width: 3.25rem;
}
</style>
