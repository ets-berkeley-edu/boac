<template>
  <b-modal
    id="advising-appointment-check-in"
    v-model="showCreateAppointmentModal"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    :no-close-on-backdrop="true"
    @cancel.prevent="cancel"
    @hide.prevent="cancel"
    @shown="putFocusNextTick('are-you-sure-confirm')">
    <div>
      <form @submit.prevent="create()">
        <div class="ml-3 mr-3">
          <div v-if="student">
            {{ student.label }}
          </div>
          <div v-if="!student" class="d-flex">
            <div>
              <label
                for="appointment-student"
                class="font-size-14 input-label text mt-2">
                <span class="sr-only">Select a </span><span class="font-weight-bolder">Student</span> (name or SID)
                <span class="sr-only">(expect auto-suggest based on what you enter)</span>
              </label>
            </div>
            <div class="mb-2">
              <Autocomplete
                id="appointment-student"
                :key="resetAutoCompleteKey"
                class="w-75"
                :demo-mode-blur="true"
                :on-esc-form-input="cancelModal"
                :show-add-button="true"
                :source="studentsByNameOrSid"
                @input="addStudent" />
            </div>
          </div>
          <div class="d-flex">
            <div>
              Reason:
            </div>
            <div>
              <AppointmentTopics
                class="mt-2 mr-3 mb-1 ml-3"
                :disabled="isSaving"
                :function-add="addTopic"
                :function-remove="removeTopic" />
            </div>
          </div>
          <div class="d-flex">
            <div>
              <label for="appointment-details" class="pb-2">Additional Information:</label>
            </div>
            <div>
              <input
                id="appointment-details"
                v-model="details"
                type="text"
                maxlength="255"
                required>
            </div>
          </div>
        </div>
        <div class="modal-footer pl-0 mr-2">
          <b-btn
            id="create-confirm"
            class="btn-primary-color-override"
            variant="primary"
            :disabled="!trim(details).length"
            @click.prevent="create()">
            Save
          </b-btn>
          <b-btn
            id="create-cancel"
            variant="link"
            @click.prevent="cancelModal()">
            Cancel
          </b-btn>
        </div>
      </form>
    </div>
  </b-modal>
</template>

<script>
import AppointmentTopics from "@/components/appointment/AppointmentTopics";
import Autocomplete from '@/components/util/Autocomplete';
import Util from '@/mixins/Util';
import Validator from '@/mixins/Validator';
import { findStudentsByNameOrSid } from '@/api/student';

export default {
  name: 'CreateAppointmentModal',
  components: {AppointmentTopics, Autocomplete},
  mixins: [Util, Validator],
  props: {
    createAppointment: {
      type: Function,
      required: false
    },
    cancel: {
      type: Function,
      required: true
    },
    showModal: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    details: '',
    isSaving: false,
    resetAutoCompleteKey: undefined,
    showCreateAppointmentModal: false,
    student: undefined,
    topics: []
  }),
  watch: {
    showModal(value) {
      this.showCreateAppointmentModal = value;
    }
  },
  created() {
    this.reset();
    this.showCreateAppointmentModal = this.showModal;
  },
  methods: {
    addStudent(student) {
      this.student = student;
    },
    addTopic(topic) {
      this.topics.push(topic);
    },
    cancelModal() {
      this.cancel();
      this.reset();
    },
    create: function() {
      this.saving = true;
      this.createAppointment(this.details, this.student.sid, this.topics);
      this.showCreateAppointmentModal = false;
      this.saving = false;
      this.reset();
    },
    removeTopic(topic) {
      console.log('Remove ' + topic);
    },
    reset() {
      this.details = '';
      this.resetAutoCompleteKey = undefined;
    },
    studentsByNameOrSid(query, limit) {
      return new Promise(resolve => findStudentsByNameOrSid(query, limit).then(students => resolve(students)));
    }
  }
};
</script>
