<template>
  <v-dialog v-model="showEditTopicModal" width="auto">
    <v-card
      max-width="400"
      title="Create Topic"
    >
      <v-card-actions>
        <div class="text-field-width d-block">
          <v-text-field
            id="topic-label"
            v-model="topic"
            aria-describedby="input-live-help topic-label-error"
            variant="outlined"
            required
          >
          </v-text-field>
        </div>
      </v-card-actions>
      <div id="topic-label-error" class="font-size-14 mt-0 pl-2 pt-2">
        <span v-if="!isValidLabel">Label must be {{ minLabelLength }} or more characters.</span>
        <span v-if="isLabelReserved">Sorry, the label '{{ _trim(topic) }}' is assigned to an existing topic.</span>
      </div>
      <div class="faint-text font-size-14 pl-2 pt-2">
        <span v-if="!isLabelReserved && isValidLabel" id="input-live-help">
          {{ maxLabelLength }} character limit <span v-if="topic.length">({{ maxLabelLength - topic.length }} left)</span>
        </span>
      </div>
      <v-spacer></v-spacer>
      <v-card-actions>
        <form @submit.prevent="save">
          <v-btn
            id="topic-save"
            variant="flat"
            :disabled="disableSaveButton"
            @click.prevent="save"
          >
            Save
          </v-btn>
          <v-btn
            id="cancel"
            variant="outlined"
            :disabled="isSaving"
            @click.stop="cancel"
          >
            Cancel
          </v-btn>
        </form>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {createTopic} from '@/api/topics'

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

.text-field-width {
  width: 350px;
}
</style>
