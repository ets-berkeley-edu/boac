<template>
  <form id="unit-requirement-form" @submit.prevent="create">
    <div class="d-flex flex-column pb-3">
      <label
        id="label-of-name-input"
        for="unit-requirement-name-input"
        class="font-weight-bolder"
      >Fulfillment Requirement Name (required)</label>
      <input
        id="unit-requirement-name-input"
        v-model="name"
        class="form-control unit-requirement-name"
        aria-labelledby="label-of-name-input"
        :aria-invalid="!name"
        aria-required="true"
        maxlength="255"
        required
        type="text"
      />
    </div>
    <div class="d-flex flex-column pb-3">
      <label
        id="label-of-min-units-input"
        for="unit-requirement-min-units-input"
        class="font-weight-bolder"
      >Minimum Units (required)</label>
      <input
        id="unit-requirement-min-units-input"
        v-model.number="minUnits"
        class="form-control unit-requirement-min-units"
        aria-labelledby="label-of-min-units-input"
        :aria-invalid="!minUnits"
        aria-required="true"
        maxlength="2"
        required
        type="number"
      />
    </div>
    <b-btn
      v-if="editMode === 'createUnitRequirement'"
      id="create-unit-requirement-btn"
      :disabled="!name || !minUnits"
      class="btn-primary-color-override"
      variant="primary"
      @click.prevent="create"
    >
      Create Unit Requirement
    </b-btn>
    <b-btn
      v-if="editMode === 'updateUnitRequirement'"
      id="update-unit-requirement-btn"
      :disabled="!name || !minUnits"
      class="btn-primary-color-override"
      variant="primary"
      @click.prevent="save"
    >
      Save Unit Requirement
    </b-btn>
    <b-btn
      id="create-appointment-cancel"
      variant="link"
      @click.prevent="cancel"
    >
      Cancel
    </b-btn>
  </form>
</template>

<script>
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'

export default {
  name: 'EditUnitRequirement',
  mixins: [Context, DegreeEditSession, Util],
  data: () => ({
    name: undefined,
    minUnits: undefined
  }),
  created() {
    this.alertScreenReader('Unit requirement form is open')
  },
  methods: {
    cancel() {
      this.setEditMode()
      this.reset()
    },
    create() {
      this.saving = true
      this.createUnitRequirement({
        name: this.name,
        minUnits: this.minUnits
      })
      this.saving = false
      this.reset()
    },
    reset() {
      this.name = undefined
      this.minUnits = undefined
    },
    save() {
      this.saving = true
      this.updateUnitRequirement(
        this.name,
        this.minUnits
      )
      this.saving = false
      this.reset()
    },
  }
}
</script>

<style scoped>
.unit-requirement-name {
  width: 22rem;
}
.unit-requirement-min-units {
  width: 4rem;
}
</style>
