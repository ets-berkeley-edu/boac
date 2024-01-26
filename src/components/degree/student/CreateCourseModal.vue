<template>
  <div>
    <div class="font-size-14">
      <b-btn
        :id="`create-course-under-parent-category-${parentCategory.id}`"
        class="font-weight-500 p-0"
        :disabled="disableButtons"
        variant="link"
        @click.prevent="openModal"
      >
        <font-awesome class="font-size-16" icon="plus" /> Manually Create Course
      </b-btn>
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
            <div class="faint-text mb-3"><span class="sr-only">Course name has a </span>255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></div>
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
              label-class="font-weight-bolder mb-1 pr-2"
              :on-submit="save"
              :set-units-lower="setUnits"
              :units-lower="units"
            />
          </div>
          <div class="pb-3">
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
              @keypress.enter="save"
            />
          </div>
          <div class="pb-3">
            <AccentColorSelect
              :accent-color="accentColor"
              :on-change="value => accentColor = value"
            />
          </div>
          <label for="course-note-textarea" class="font-weight-bolder">
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

<script>
import AccentColorSelect from '@/components/degree/student/AccentColorSelect'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import ModalHeader from '@/components/util/ModalHeader'
import UnitsInput from '@/components/degree/UnitsInput'
import Util from '@/mixins/Util'

export default {
  name: 'CreateCourseModal',
  components: {AccentColorSelect, ModalHeader, UnitsInput},
  mixins: [DegreeEditSession, Util],
  props: {
    parentCategory: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    accentColor: undefined,
    error: undefined,
    grade: undefined,
    isSaving: false,
    name: '',
    note: '',
    showModal: false,
    units: undefined
  }),
  computed: {
    disableSaveButton() {
      return this.isSaving || !!this.unitsErrorMessage || !this._trim(this.name)
    },
    unitsErrorMessage() {
      const isEmpty = this._isEmpty(this._trim(this.units))
      return isEmpty ? null : this.validateUnitRange(this.units, undefined, 10).message
    }
  },
  destroyed() {
    this.closeModal()
  },
  methods: {
    cancel() {
      this.closeModal()
      this.$announcer.polite('Canceled')
    },
    closeModal() {
      this.accentColor = undefined,
      this.error = undefined
      this.grade = undefined
      this.isSaving = false
      this.name = ''
      this.note = ''
      this.selectedUnitRequirements = []
      this.showModal = false
      this.units = undefined
      this.setDisableButtons(false)
    },
    openModal() {
      this.showModal = true
      this.setDisableButtons(true)
      this.$announcer.polite('Create course dialog opened')
    },
    save() {
      if (!this.disableSaveButton) {
        this.isSaving = true
        this.createCourse({
          accentColor: this.accentColor,
          grade: this._trim(this.grade),
          name: this._trim(this.name),
          note: this._trim(this.note),
          parentCategoryId: this.parentCategory.id,
          unitRequirementIds: this._map(this.selectedUnitRequirements, 'id'),
          units: this.units
        }).then(course => {
          this.closeModal()
          this.$announcer.polite(`Course ${course.name} created`)
          this.putFocusNextTick(`assign-course-${course.id}-dropdown`, 'button')
        })
      }
    },
    setUnits(units) {
      this.units = units
    }
  }
}
</script>

<style scoped>
.grade-input {
  width: 3rem;
}
</style>
