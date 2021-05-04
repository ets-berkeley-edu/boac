<template>
  <div id="edit-unassigned-course" class="border border-1 mb-1 pb-3 px-2 rounded">
    <div>
      <div class="font-weight-500 my-2">
        Units
      </div>
      <div>
        <b-form-input
          :id="`course-units-input`"
          v-model="units"
          class="course-units-input"
          :disabled="isSaving"
          maxlength="3"
          trim
          @keypress.enter="update"
        />
      </div>
      <div class="font-weight-500 my-2">
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
    <div class="d-flex mt-3">
      <div>
        <b-btn
          id="update-note-btn"
          class="btn-primary-color-override"
          :disabled="disableSaveButton"
          variant="primary"
          @click="update"
        >
          <span v-if="isSaving">
            <font-awesome class="mr-1" icon="spinner" spin /> Saving
          </span>
          <span v-if="!isSaving">Update</span>
        </b-btn>
      </div>
      <div>
        <b-btn
          id="cancel-update-note-btn"
          :disabled="isSaving"
          variant="link"
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
import Util from '@/mixins/Util'

export default {
  name: 'EditCourse',
  mixins: [DegreeEditSession, Util],
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
    }
  },
  data: () => ({
    isSaving: false,
    note: '',
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
    update() {
      if (!this.disableSaveButton) {
        this.isSaving = true
        this.updateCourse({
          courseId: this.course.id,
          note: this.note,
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
