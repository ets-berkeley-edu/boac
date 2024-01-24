<template>
  <b-modal
    v-model="showEditTopicModal"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    :no-close-on-backdrop="true"
    :ok-disabled="isSaving"
    @cancel.prevent="cancel"
    @hide.prevent="cancel"
    @shown="$putFocusNextTick('modal-header')"
  >
    <div>
      <ModalHeader>
        Create Topic
      </ModalHeader>
      <div class="modal-body pl-4 pr-5">
        <div class="topic-label-input-container">
          <label for="topic-label" class="font-size-18 font-weight-bolder mb-1">Label</label>
          <!-- TODO: Fix vue/no-mutating-props offenders below. -->
          <!-- eslint-disable vue/no-mutating-props -->
          <b-form-input
            id="topic-label"
            v-model="topic"
            aria-describedby="input-live-help topic-label-error"
            :maxlength="maxLabelLength"
            :state="!isLabelReserved && isValidLabel"
            required
            size="lg"
          ></b-form-input>
          <b-form-invalid-feedback id="topic-label-error" class="font-size-14 mt-0 pl-2 pt-2">
            <span v-if="!isValidLabel">Label must be {{ minLabelLength }} or more characters.</span>
            <span v-if="isLabelReserved">Sorry, the label '{{ _trim(topic) }}' is assigned to an existing topic.</span>
          </b-form-invalid-feedback>
          <div class="faint-text font-size-14 pl-2 pt-2">
            <span v-if="!isLabelReserved && isValidLabel" id="input-live-help">
              {{ maxLabelLength }} character limit <span v-if="topic.length">({{ maxLabelLength - topic.length }} left)</span>
            </span>
          </div>
        </div>
      </div>
      <!-- eslint-enable vue/no-mutating-props -->
      <div class="modal-footer">
        <form @submit.prevent="save">
          <b-btn
            id="topic-save"
            class="btn-primary-color-override"
            :disabled="disableSaveButton"
            variant="primary"
            @click.prevent="save"
          >
            Save
          </b-btn>
          <b-btn
            id="cancel"
            class="pl-3"
            :disabled="isSaving"
            variant="link"
            @click.stop="cancel"
          >
            Cancel
          </b-btn>
        </form>
      </div>
    </div>
  </b-modal>
</template>

<script>
import Context from '@/mixins/Context'
import ModalHeader from '@/components/util/ModalHeader'
import Util from '@/mixins/Util'
import {createTopic} from '@/api/topics'

export default {
  name: 'EditTopicModal',
  components: {ModalHeader},
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
    }
  },
  data: () => ({
    error: undefined,
    isSaving: false,
    maxLabelLength: 50,
    minLabelLength: 3,
    showEditTopicModal: false,
    topic: undefined
  }),
  computed: {
    disableSaveButton() {
      return !this.isValidLabel || this.isSaving || this.isLabelReserved
    },
    isLabelReserved() {
      return !!this._find(this.allTopics, t => {
        const trimmed = this._trim(this.topic)
        return t.topic.toLowerCase() === trimmed.toLowerCase()
      })
    },
    isValidLabel() {
      return this._trim(this.topic).length >= this.minLabelLength
    }
  },
  created() {
    this.topic = ''
    this.showEditTopicModal = true
  },
  methods: {
    cancel() {
      this.showEditTopicModal = false
      this.onCancel()
    },
    save() {
      this.isSaving = true
      this.topic = this._trim(this.topic)
      createTopic(this.topic).then(data => {
        this.afterSave(data)
        this.isSaving = false
        this.showEditTopicModal = false
      })
    }
  }
}
</script>

<style scoped>
.topic-label-input-container {
  min-height: 110px;
}
</style>
