<template>
  <div>
    <div>
      <label id="add-appointment-topic-label" class="font-weight-bold mt-2" for="add-appointment-topic">
        Topic Categories
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
            <span class="pill pill-attachment text-uppercase text-nowrap">
              {{ addedTopic }}
              <b-btn
                :id="`remove-appointment-topic-${index}`"
                :disabled="disabled"
                variant="link"
                class="px-0 pt-1"
                :aria-labelledby="`remove-appointment-topic-${index}-label`"
                tabindex="0"
                @click.prevent="remove(addedTopic)">
                <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
              </b-btn>
              <label :id="`remove-appointment-topic-${index}-label`" class="sr-only" :for="`remove-appointment-topic-${index}`">
                remove topic {{ topics[index] }}
              </label>
            </span>
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
        this.putFocusNextTick('add-topic-select-list');
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
