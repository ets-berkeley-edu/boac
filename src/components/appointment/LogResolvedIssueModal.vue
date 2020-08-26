<template>
  <b-modal
    id="log-resolved-issue"
    v-model="showLogResolvedIssueModal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="cancel"
    @hide.prevent="cancel">
    <div>
      <div class="modal-header">
        <h3 class="ml-2">
          <span aria-live="polite" role="alert">Log Resolved Issue</span>
        </h3>
      </div>
      <form @submit.prevent="log">
        <div class="font-weight-500 ml-4 mr-3 mt-2">
          <div>
            <label
              for="log-resolved-issue-student-input"
              class="font-size-14 input-label text mt-2">
              <span class="sr-only">Select a </span><span class="font-weight-bolder">Student</span>
              <span v-if="!student"> (name or SID)</span>
              <span class="sr-only">(expect auto-suggest based on what you enter)</span>
            </label>
          </div>
          <div v-if="student" class="d-inline-block">
            <AppointmentStudentPill
              :remove-student="removeStudent"
              :student="student" />
          </div>
          <div v-if="!student">
            <div class="mb-2">
              <Autocomplete
                id="log-resolved-issue-student"
                :key="resetAutoCompleteKey"
                :demo-mode-blur="true"
                :on-esc-form-input="cancelModal"
                :show-add-button="true"
                :source="studentsByNameOrSid"
                class="w-75"
                @input="addStudent" />
            </div>
          </div>
          <div v-if="isStudentInWaitlist" class="mt-2 text-danger">
            <font-awesome icon="exclamation-triangle" class="pr-1" />
            This student is already in the Drop-In Waitlist.
          </div>
          <div class="mt-2">
            <AppointmentTopics
              :disabled="isSaving"
              :function-add="addTopic"
              :function-remove="removeTopic"
              :topics="topics" />
          </div>
          <div class="mb-4 mr-3 mt-1">
            <label for="log-resolved-issue-details" class="font-size-14 input-label text">
              <span class="font-weight-bolder">Issue &amp; Resolution</span>
            </label>
            <div id="log-resolved-issue-details">
              <RichTextEditor
                :initial-value="details || ''"
                :disabled="isSaving"
                :is-in-modal="true"
                :on-value-update="d => details = d" />
            </div>
          </div>
        </div>
        <div class="modal-footer pl-0 mt-2">
          <b-btn
            id="log-resolved-issue-confirm"
            :disabled="!student || isStudentInWaitlist || !topics.length || !trim(details).length"
            class="btn-primary-color-override"
            variant="primary"
            @click.prevent="log">
            Log Resolved Issue
          </b-btn>
          <b-btn
            id="log-resolved-issue-cancel"
            variant="link"
            @click.prevent="cancelModal">
            Cancel
          </b-btn>
        </div>
      </form>
    </div>
  </b-modal>
</template>

<script>
import AppointmentStudentPill from '@/components/appointment/AppointmentStudentPill'
import AppointmentTopics from '@/components/appointment/AppointmentTopics'
import Autocomplete from '@/components/util/Autocomplete'
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import RichTextEditor from '@/components/util/RichTextEditor'
import Util from '@/mixins/Util'
import Validator from '@/mixins/Validator'
import { findStudentsByNameOrSid } from '@/api/student'

export default {
  name: 'LogResolvedIssueModal',
  components: {AppointmentStudentPill, AppointmentTopics, Autocomplete, RichTextEditor},
  mixins: [Berkeley, Context, Util, Validator],
  props: {
    cancel: {
      type: Function,
      required: true
    },
    logResolvedIssue: {
      type: Function,
      required: true
    },
    showModal: {
      type: Boolean,
      required: true
    },
    waitlistUnresolved: {
      type: Array,
      required: true
    }
  },
  data: () => ({
    details: '',
    isSaving: false,
    resetAutoCompleteKey: undefined,
    showLogResolvedIssueModal: false,
    student: undefined,
    topics: []
  }),
  computed: {
    isStudentInWaitlist() {
      return this.student && !!this.find(this.waitlistUnresolved, (s) => s.student.uid === this.student.uid)
    }
  },
  watch: {
    showModal(value) {
      this.showLogResolvedIssueModal = value
    }
  },
  created() {
    this.reset()
    this.showLogResolvedIssueModal = this.showModal
    this.putFocusNextTick('log-resolved-issue-student-input')
    this.alertScreenReader('Log resolved issue form is open')
  },
  methods: {
    addStudent(student) {
      if (student) {
        this.student = student
        this.alertScreenReader(`Student ${this.student.label} selected`)
        this.putFocusNextTick('add-topic-select-list')
      }
    },
    addTopic(topic) {
      this.topics.push(topic)
    },
    cancelModal() {
      this.cancel()
      this.reset()
    },
    log() {
      this.saving = true
      this.logResolvedIssue(
        this.details,
        this.student,
        this.topics,
        this.$currentUser.uid
      )
      this.showLogResolvedIssueModal = false
      this.saving = false
      this.reset()
    },
    removeStudent() {
      this.alertScreenReader(`${this.student.label} removed`)
      this.student = undefined
    },
    removeTopic(topic) {
      const index = this.indexOf(this.topics, topic)
      if (index !== -1) {
        this.topics.splice(index, 1)
      }
    },
    reset() {
      this.details = ''
      this.resetAutoCompleteKey = undefined
    },
    studentsByNameOrSid(query, limit) {
      return new Promise(resolve => findStudentsByNameOrSid(query, limit).then(students => resolve(students)))
    }
  }
}
</script>
