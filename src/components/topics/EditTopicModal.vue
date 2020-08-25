<template>
  <b-modal
    id="edit-topic-modal"
    v-model="showEditTopicModal"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    :no-close-on-backdrop="true"
    :ok-disabled="isSaving"
    @cancel.prevent="cancel"
    @hide.prevent="cancel">
    <div>
      <div class="modal-header">
        <h3 id="are-you-sure-header" class="new-note-header pl-2">{{ topic.id ? 'Edit' : 'Create' }} Topic</h3>
      </div>
      <div class="modal-body pl-4 pr-5">
        <div class="topic-label-input-container">
          <label for="topic-label" class="font-size-18 font-weight-bolder mb-1">Label</label>
          <b-form-input
            id="topic-label"
            v-model="topic.topic"
            aria-describedby="input-live-help topic-label-error"
            :maxlength="maxLabelLength"
            :state="!isLabelReserved && isValidLabel"
            required
            size="lg"></b-form-input>
          <b-form-invalid-feedback id="topic-label-error" class="font-size-14 mt-0 pl-2 pt-2">
            <span v-if="!isValidLabel">Label must be {{ minLabelLength }} or more characters.</span>
            <span v-if="isLabelReserved">Sorry, the label '{{ $_.trim(topic.topic) }}' is assigned to an existing topic.</span>
          </b-form-invalid-feedback>
          <div class="faint-text font-size-14 pl-2 pt-2">
            <span v-if="!isLabelReserved && isValidLabel" id="input-live-help">
              {{ maxLabelLength }} character limit <span v-if="topic.topic.length">({{ maxLabelLength - topic.topic.length }} left)</span>
            </span>
          </div>
        </div>
        <h4 class="font-size-18 font-weight-bolder mb-0 pt-2">Type</h4>
        <span class="font-size-12 text-secondary">You must choose at least one.</span>
        <b-form-checkbox
          id="topic-available-in-notes"
          v-model="topic.availableInNotes"
          class="m-2"
          name="topic-available-in-notes">
          Note Topic
        </b-form-checkbox>
        <b-form-checkbox
          id="topic-available-in-appointments"
          v-model="topic.availableInAppointments"
          class="m-2"
          name="topic-available-in-appointments">
          Appointment Reason
        </b-form-checkbox>
      </div>
      <div class="modal-footer">
        <form @submit.prevent="save">
          <b-btn
            id="topic-save"
            class="btn-primary-color-override"
            :disabled="disableSaveButton"
            variant="primary"
            @click.prevent="save">
            Save
          </b-btn>
          <b-btn
            id="cancel"
            class="pl-3"
            :disabled="isSaving"
            variant="link"
            @click.stop="cancel">
            Cancel
          </b-btn>
        </form>
      </div>
    </div>
  </b-modal>
</template>

<script>
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';
import {createTopic, updateTopic} from '@/api/topics';

export default {
  name: 'EditTopicModal',
  mixins: [Context, Util],
  props: {
    afterSave: {
      required: true,
      type: Function
    },
    allTopics: {
      required: true,
      type: Array
    },
    onCancel: {
      required: true,
      type: Function
    },
    topic: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    error: undefined,
    isSaving: false,
    maxLabelLength: 50,
    minLabelLength: 3,
    showEditTopicModal: false
  }),
  computed: {
    disableSaveButton() {
      return !this.isValidLabel || this.isSaving || (!this.topic.availableInAppointments && !this.topic.availableInNotes) || this.isLabelReserved;
    },
    isLabelReserved() {
      return !!this.$_.find(this.allTopics, t => {
        const trimmed = this.$_.trim(this.topic.topic);
        return t.id !== this.topic.id && (t.topic.toLowerCase() === trimmed.toLowerCase());
      });
    },
    isValidLabel() {
      return this.$_.trim(this.topic.topic).length >= this.minLabelLength;
    }
  },
  created() {
    this.showEditTopicModal = true;
    this.putFocusNextTick('topic-label');
  },
  methods: {
    cancel() {
      this.showEditTopicModal = false;
      this.onCancel();
    },
    save() {
      this.isSaving = true;
      this.topic.topic = this.$_.trim(this.topic.topic);
      if (this.topic.id) {
        updateTopic(
          this.topic.id,
          this.topic.availableInAppointments,
          this.topic.availableInNotes,
          this.topic.topic
        ).then(data => {
          this.afterSave(data);
          this.isSaving = false;
          this.showEditTopicModal = false;
        });
      } else {
        createTopic(this.topic.availableInAppointments, this.topic.availableInNotes, this.topic.topic).then(data => {
          this.afterSave(data);
          this.isSaving = false;
          this.showEditTopicModal = false;
        })
      }
    }
  }
}
</script>

<style scoped>
.topic-label-input-container {
  min-height: 110px;
}
</style>
