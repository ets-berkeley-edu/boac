<template>
  <div>
    <div>
      <label for="add-topic-select-list" class="font-size-14 input-label text mt-2">
        <span class="font-weight-bolder">Reason</span>
      </label>
    </div>
    <b-container class="pl-0 ml-0">
      <b-form-row class="pb-1">
        <b-col cols="9">
          <b-form-select
            v-if="topicOptions.length"
            id="add-topic-select-list"
            :key="topics.length"
            v-model="selected"
            :disabled="disabled"
            role="listbox"
            aria-label="Use up and down arrows to review topics. Hit enter to select a topic."
            @input="add">
            <template v-slot:first>
              <option :value="null">Select...</option>
            </template>
            <option
              v-for="option in topicOptions"
              :key="option.value"
              :disabled="option.disabled"
              :value="option.value">
              {{ option.text }}
            </option>
          </b-form-select>
        </b-col>
      </b-form-row>
      <div>
        <ul
          id="appointment-topics-list"
          class="pill-list pl-0"
          aria-labelledby="appointment-topics-label">
          <li
            v-for="(addedTopic, index) in topics"
            :id="`appointment-topic-${index}`"
            :key="index">
            <div class="d-inline-block">
              <div class="d-flex pill pill-topic text-uppercase text-nowrap">
                <div :id="`topic-label-${index}`" class="added-topic">
                  {{ addedTopic }}
                </div>
                <div class="remove-topic-container mr-2">
                  <b-btn
                    :id="`remove-appointment-topic-${index}`"
                    :disabled="disabled"
                    variant="link"
                    class="m-0 p-0"
                    @click.prevent="remove(addedTopic)">
                    <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
                    <span class="sr-only">Remove topic "{{ topics[index] }}"</span>
                  </b-btn>
                </div>
              </div>
            </div>
          </li>
        </ul>
        <label id="appointment-topics-label" class="sr-only" for="appointment-topics-list">
          topics
        </label>
      </div>
    </b-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import { getTopicsForAppointments } from '@/api/topics'

export default {
  name: 'AppointmentTopics',
  mixins: [Context, Util],
  props: {
    appointmentId: {
      default: undefined,
      type: Number,
      required: false
    },
    disabled: {
      required: false,
      type: Boolean
    },
    functionAdd: {
      type: Function,
      required: true
    },
    functionRemove: {
      type: Function,
      required: true
    },
    topics: {
      type: Array,
      required: true
    }
  },
  data: () => ({
    selected: null,
    topicOptions: []
  }),
  created() {
    getTopicsForAppointments().then(rows => {
      this.$_.each(rows, row => {
        const topic = row['topic']
        this.topicOptions.push({
          text: topic,
          value: topic,
          disabled: this.$_.includes(this.topics, topic)
        })
      })
    })
  },
  methods: {
    add(topic) {
      // Reset the dropdown
      this.selected = null
      if (topic) {
        this.setDisabled(topic, true)
        this.functionAdd(topic)
        // TODO: do not mutate prop
        this.topics.sort()  // eslint-disable-line vue/no-mutating-props
        this.putFocusNextTick('add-topic-select-list')
        this.alertScreenReader(`"${topic}" added.`)
      }
    },
    remove(topic) {
      this.setDisabled(topic, false)
      this.functionRemove(topic)
      this.putFocusNextTick('add-topic-select-list')
      this.alertScreenReader(`"${topic}" removed.`)
    },
    setDisabled(topic, disable) {
      const option = this.$_.find(this.topicOptions, ['value', topic])
      this.$_.set(option, 'disabled', disable)
    }
  }
}
</script>

<style scoped>
.added-topic {
  padding: 5px 2px 6px 12px;
}
.pill-topic {
  height: 32px;
}
</style>
