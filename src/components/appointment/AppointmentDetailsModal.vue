<template>
  <b-modal
    v-model="showDetailsModal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="close"
    @hide.prevent="close"
    @shown="$putFocusNextTick('modal-header')"
  >
    <div>
      <ModalHeader>
        <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.name }}</span>
      </ModalHeader>
      <div class="modal-body w-100">
        <b-container fluid>
          <div class="mt-2">
            <label class="font-size-14 font-weight-bolder text-nowrap m-0" for="appointment-created-at">
              Arrival Time
            </label>
            <div id="appointment-created-at">
              {{ $moment(appointment.createdAt).format('LT') }}
            </div>
          </div>
          <div class="mt-2">
            <AppointmentTopics
              :disabled="isSaving"
              :function-add="addTopic"
              :function-remove="removeTopic"
              :topics="topics"
            />
          </div>
          <div class="mb-4 mr-3 mt-1">
            <div id="appointment-details">
              <RichTextEditor
                :initial-value="details || ''"
                :disabled="isSaving"
                :is-in-modal="true"
                label="Additional Information"
                :on-value-update="d => details = d"
              />
            </div>
          </div>
        </b-container>
      </div>
      <div class="modal-footer">
        <b-btn
          v-if="!$currentUser.isAdmin"
          id="btn-appointment-details-update"
          class="pl-2"
          variant="primary"
          :disabled="!topics.length || !_trim(details).length"
          @click.stop="update"
        >
          Update
        </b-btn>
        <b-btn
          id="btn-appointment-cancel"
          class="pl-2"
          variant="link"
          @click.stop="close"
        >
          Close
        </b-btn>
      </div>
    </div>
  </b-modal>
</template>

<script>
import AppointmentTopics from '@/components/appointment/AppointmentTopics'
import Context from '@/mixins/Context'
import ModalHeader from '@/components/util/ModalHeader'
import RichTextEditor from '@/components/util/RichTextEditor'
import Util from '@/mixins/Util'

export default {
  name: 'AppointmentDetailsModal',
  components: {AppointmentTopics, ModalHeader, RichTextEditor},
  mixins: [Context, Util],
  props: {
    appointment: {
      type: Object,
      required: true
    },
    close: {
      type: Function,
      required: true
    },
    showModal: {
      type: Boolean,
      required: true
    },
    student: {
      type: Object,
      required: true
    },
    updateAppointment: {
      type: Function,
      required: false
    },
  },
  data: () => ({
    details: '',
    isSaving: false,
    showDetailsModal: false,
    topics: []
  }),
  watch: {
    showModal(value) {
      this.showDetailsModal = value
    }
  },
  created() {
    this.details = this.appointment.details
    this.topics = this._clone(this.appointment.topics)
    this.showDetailsModal = this.showModal
    this.$putFocusNextTick('modal-header')
    this.$announcer.polite('Appointment details form is open')
  },
  methods: {
    addTopic(topic) {
      this.topics.push(topic)
    },
    removeTopic(topic) {
      const index = this._indexOf(this.topics, topic)
      if (index !== -1) {
        this.topics.splice(index, 1)
      }
    },
    update() {
      this.isSaving = true
      this.updateAppointment(
        this.details,
        this.topics,
      )
      this.showDetailsModal = false
      this.isSaving = false
    }
  }
}
</script>
