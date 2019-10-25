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
            id="add-topic-select-list"
            v-if="topicOptions.length"
            :key="topics.length"
            v-model="selected"
            :disabled="disabled"
            @input="add"
            role="listbox"
            aria-label="Use up and down arrows to review topics. Hit enter to select a topic.">
            <template v-slot:first>
              <option :value="null" disabled>Select...</option>
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
                    :aria-labelledby="`remove-appointment-topic-${index}-label`"
                    @click.prevent="remove(addedTopic)"
                    variant="link"
                    class="m-0 p-0"
                    tabindex="0">
                    <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
                  </b-btn>
                  <label :id="`remove-appointment-topic-${index}-label`" :for="`remove-appointment-topic-${index}`" class="sr-only">
                    Remove topic "{{ topics[index] }}"
                  </label>
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
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { getAllTopics } from '@/api/appointments';

export default {
  name: 'AppointmentTopics',
  mixins: [Context, UserMetadata, Util],
  props: {
    appointmentId: {
      type: Number,
      required: false
    },
    disabled: {
      default: false,
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
    focusAfterTopicAdd: {
      default: 'add-topic-select-list',
      type: String,
      required: false,
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
    getAllTopics().then(topics => {
      this.each(topics, topic => {
        this.topicOptions.push({
          text: topic,
          value: topic,
          disabled: false
        })
      });
    });
  },
  methods: {
    add(topic) {
      // Reset the dropdown
      this.selected = null;
      if (topic) {
        this.setDisabled(topic, true);
        this.functionAdd(topic);
        this.putFocusNextTick(this.focusAfterTopicAdd);
        this.alertScreenReader(`Topic ${topic} added.`);
      }
    },
    remove(topic) {
      this.setDisabled(topic, false);
      this.functionRemove(topic);
      this.putFocusNextTick('add-topic-select-list');
      this.alertScreenReader(`Topic ${topic} removed.`);
    },
    setDisabled(topic, disable) {
      const option = this.find(this.topicOptions, ['value', topic]);
      this.set(option, 'disabled', disable);
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
