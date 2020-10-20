<template>
  <b-modal
    id="advising-appointment-create"
    v-model="showCreateAppointmentModal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="cancel"
    @hide.prevent="cancel">
    <div>
      <div class="modal-header">
        <h3 class="ml-2">
          <span aria-live="polite" role="alert"><span class="sr-only">Create new </span>Advising Appointment</span>
        </h3>
      </div>
      <form @submit.prevent="create">
        <div class="font-weight-500 ml-4 mr-3 mt-2">
          <div>
            <label
              for="appointment-student-input"
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
              <span id="appointment-student-input-label" class="sr-only">Select student for appointment. Expect auto-suggest as you type name or SID.</span>
              <Autocomplete
                id="appointment-student"
                :key="resetAutoCompleteKey"
                class="w-75"
                :demo-mode-blur="true"
                input-labelled-by=""
                :on-esc-form-input="cancelModal"
                :show-add-button="true"
                :source="studentsByNameOrSid"
                @input="addStudent"
              />
            </div>
          </div>
          <div v-if="isStudentInWaitlist" class="mt-2 text-danger">
            <font-awesome icon="exclamation-triangle" class="pr-1" />
            This student is already in the Drop-In Waitlist.
          </div>
          <div v-if="advisors">
            <label
              for="create-modal-advisor-select"
              class="font-size-14 input-label text mt-2">
              <span class="sr-only">Select an </span><span class="font-weight-bolder">Advisor</span> (optional)
            </label>
            <b-col v-if="availableAdvisors.length" cols="9" class="pl-0">
              <b-form-select
                id="create-modal-advisor-select"
                v-model="selectedAdvisorUid">
                <template v-slot:first>
                  <option :value="null">Select...</option>
                </template>
                <option
                  v-for="advisor in availableAdvisors"
                  :key="advisor.uid"
                  :value="advisor.uid">
                  {{ advisor.name }}
                </option>
              </b-form-select>
            </b-col>
            <div v-if="!availableAdvisors.length" class="has-error pb-1 pt-1">
              Sorry, no advisors are on duty.
            </div>
          </div>
          <div class="mt-2">
            <AppointmentTopics
              :disabled="isSaving"
              :function-add="addTopic"
              :function-remove="removeTopic"
              :topics="topics" />
          </div>
          <div class="mb-4 mr-3 mt-1">
            <div id="appointment-details">
              <RichTextEditor
                :initial-value="details || ''"
                :disabled="isSaving"
                :is-in-modal="true"
                label="Description"
                :on-value-update="d => details = d" />
            </div>
          </div>
        </div>
        <div class="modal-footer pl-0 mt-2">
          <b-btn
            id="create-appointment-confirm"
            :disabled="!student || isStudentInWaitlist || !topics.length || !trim(details).length"
            class="btn-primary-color-override"
            variant="primary"
            @click.prevent="create">
            Make Appointment
          </b-btn>
          <b-btn
            id="create-appointment-cancel"
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
  name: 'CreateAppointmentModal',
  components: {AppointmentStudentPill, AppointmentTopics, Autocomplete, RichTextEditor},
  mixins: [Berkeley, Context, Util, Validator],
  props: {
    advisors: {
      type: Array,
      required: true
    },
    createAppointment: {
      type: Function,
      required: false
    },
    cancel: {
      type: Function,
      required: true
    },
    deptCode: {
      type: String,
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
    availableAdvisors: [],
    details: '',
    isSaving: false,
    resetAutoCompleteKey: undefined,
    selectedAdvisorUid: null,
    showCreateAppointmentModal: false,
    student: undefined,
    topics: []
  }),
  computed: {
    isStudentInWaitlist() {
      return this.student && !!this.find(this.waitlistUnresolved, (s) => s.student.uid === this.student.uid)
    }
  },
  watch: {
    advisors() {
      this.updateAvailableAdvisors()
    },
    showModal(value) {
      this.showCreateAppointmentModal = value
    }
  },
  created() {
    this.reset()
    this.updateAvailableAdvisors()
    this.showCreateAppointmentModal = this.showModal
    this.putFocusNextTick('appointment-student-input')
    this.alertScreenReader('Create appointment form is open')
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
    create() {
      this.saving = true
      this.createAppointment(
        this.details,
        this.student,
        this.topics,
        this.selectedAdvisorUid
      )
      this.showCreateAppointmentModal = false
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
    },
    updateAvailableAdvisors() {
      this.availableAdvisors = this.$_.filter(this.advisors, a => {
        return a.available || a.uid === this.$currentUser.uid
      })
    }
  }
}
</script>
