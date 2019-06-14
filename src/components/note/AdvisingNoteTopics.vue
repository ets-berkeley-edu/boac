<template>
  <div>
    <div>
      <label id="add-note-topic-label" class="font-weight-bold mt-2" for="add-note-topic">
        Topic Categories
      </label>
    </div>
    <b-container class="pl-0 ml-0">
      <b-form-row class="pb-1">
        <b-col cols="9">
          <b-input-group>
            <span id="add-note-topic-instructions" class="sr-only">Use up and down arrows to review categories and enter to select.</span>
            <b-form-select
              id="add-topic-select-list"
              v-model="topic"
              :options="topicOptions"
              role="listbox">
            </b-form-select>
            <b-input-group-append>
              <b-button
                id="add-topic-button"
                slot="append"
                :class="{'btn-add-topic': !isTopicEmpty, 'btn-add-topic-disabled': isTopicEmpty}"
                aria-controls="note-topics-list"
                :disabled="isTopicEmpty"
                @click="addTopic">
                <font-awesome icon="plus" class="pr-1" /> Add<span class="sr-only"> Topic</span>
              </b-button>
            </b-input-group-append>
          </b-input-group>
        </b-col>
      </b-form-row>
      <div>
        <ul
          id="note-topics-list"
          class="pill-list pl-0"
          aria-labelledby="note-topics-label">
          <li
            v-for="(addedTopic, index) in topics"
            :id="`${notePrefix}-topic-${index}`"
            :key="index">
            <span class="pill pill-attachment text-uppercase text-nowrap">
              {{ addedTopic }}
              <b-btn
                :id="`remove-${notePrefix}-topic-${index}`"
                variant="link"
                class="px-0 pt-1"
                :aria-labelledby="`remove-${notePrefix}-topic-${index}-label`"
                tabindex="0"
                @click.prevent="removeTopic(addedTopic)">
                <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
              </b-btn>
              <label :id="`remove-${notePrefix}-topic-${index}-label`" class="sr-only" :for="`remove-${notePrefix}-topic-${index}`">
                remove topic {{ topics[index] }}
              </label>
            </span>
          </li>
        </ul>
        <label id="note-topics-label" class="sr-only" for="note-topics-list">
          topics
        </label>
      </div>
    </b-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import NoteEditSession from "@/mixins/NoteEditSession";
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingNoteTopics',
  mixins: [Context, NoteEditSession, Util],
  props: {
    functionAdd: {
      type: Function,
      required: true
    },
    functionRemove: {
      type: Function,
      required: true
    },
    noteId: {
      type: String,
      required: false
    },
    topics: {
      type: Array,
      required: true
    }
  },
  data: () => ({
    topic: null,
    topicOptions: [
      {text: '-- Select a category --', value: null}
    ]
  }),
  computed: {
    isTopicEmpty() {
      return !this.trim(this.topic)
    },
    notePrefix() {
      return this.noteId ? 'note-' + this.noteId : 'note';
    }
  },
  created: function() {
    this.each(this.suggestedTopics, suggestedTopic => {
      this.topicOptions.push({
        text: suggestedTopic,
        value: suggestedTopic,
        disabled: this.includes(this.topics, suggestedTopic)
      })
    });
  },
  methods: {
    addTopic() {
      if (this.trim(this.topic)) {
        this.functionAdd(this.topic);
        this.alertScreenReader(`Topic ${this.topic} added.`);
        this.setTopicOptionDisabled(this.topic, true);
        this.topic = undefined;
      }
    },
    normalizeString(str) {
      return str.toUpperCase().replace(/[^A-Z]/g, '');
    },
    removeTopic(topic) {
      this.functionRemove(topic);
      this.alertScreenReader(`Topic ${topic} removed.`);
      this.setTopicOptionDisabled(topic, false);
    },
    setTopicOptionDisabled(optionValue, disable) {
      const option = this.find(this.topicOptions, ['value', optionValue]);
      this.set(option, 'disabled', disable);
    },
    suggest() {
      if (!this.topic || this.topic.length < 2) {
        return false;
      }
      let match = this.suggestedTopics.find(t => {
        return this.normalizeString(t).indexOf(this.normalizeString(this.topic)) !== -1;
      });
      if (match) {
        this.topic = match;
        this.alertScreenReader(`Topic autocompleted: ${this.topic}`);
      }
    }
  }
}
</script>

<style scoped>
.btn-add-topic {
  background-color: #e9ecef;
  border-color: #ced4da;
  color: #000;
}
.btn-add-topic:not(:disabled) {
  cursor: pointer;
}
.btn-add-topic:hover,
.btn-add-topic:focus,
.btn-add-topic:active
{
  color: #333;
  background-color: #aaa;
}
.btn-add-topic-disabled {
  background-color: #ccc;
  border-color: #ced4da;
  color: #6c757d;
}
</style>
