<template>
  <div>
    <div id="edit-unassigned-course">
      <div class="font-weight-500 my-2">
        Note
      </div>
      <div>
        <b-form-textarea
          id="note-of-unassigned-course-textarea"
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
          class="b-dd-override"
          :disabled="!$_.trim(note)"
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
  name: 'EditUnassignedCourse',
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
      default: undefined,
      required: false,
      type: Object
    }
  },
  data: () => ({
    isSaving: false,
    note: ''
  }),
  created() {
    this.name = this.course.note
    this.putFocusNextTick('note-of-unassigned-course-textarea')
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled')
      this.afterCancel()
    },
    update() {
      this.isSaving = true
      this.updateCourseNote({
        courseId: this.course.id,
        note: this.note
      }).then(() => {
        this.$announcer.polite('Note updated')
        this.afterSave()
      })
    }
  }
}
</script>
