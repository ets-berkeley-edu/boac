<template>
  <div>
    <div>
      <label id="add-note-topic-label" class="font-weight-bold mt-2" for="add-note-topic">
        Topic Categories
      </label>
    </div>
    <b-container class="pl-0 ml-0">
      <b-form-row class="pb-1">
        <b-col cols="4">
          <b-input-group>
            <b-form-input
              id="add-note-topic"
              v-model="topic"
              aria-labelledby="add-note-topic-label"
              aria-describedby="add-note-topic-instructions"
              aria-owns="add-topic-input-list"
              type="text"
              maxlength="255"
              list="add-topic-input-list"
              @keydown.enter="addTopic">
            </b-form-input>
            <span id="add-note-topic-instructions" class="sr-only">When autocomplete results are available, use up and down arrows to review and enter to select.</span>
            <b-form-datalist id="add-topic-input-list" :options="suggestedTopics" role="listbox"></b-form-datalist>
            <b-input-group-append>
              <b-button
                id="add-topic-button"
                slot="append"
                class="btn-add-topic"
                aria-controls="note-topics-list"
                @click="addTopic">
                <i class="fas fa-plus pr-1"></i>Add<span class="sr-only"> Topic</span>
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
            id="`note-topic-${index}`"
            :key="index">
            <span class="pill pill-attachment text-uppercase text-nowrap">
              {{ addedTopic }}
              <b-btn
                :id="`remove-note-topic-${index}`"
                variant="link"
                class="px-0 pt-1"
                :aria-labelledby="`remove-note-topic-${index}-label`"
                tabindex="0"
                @click.prevent="removeTopic(addedTopic)">
                <i class="fas fa-times-circle has-error pl-2"></i>
              </b-btn>
              <label :id="`remove-note-topic-${index}-label`" class="sr-only" :for="`remove-note-topic-${index}`">
                remove topic {{ topics[index] }}
              </label>
            </span>
          </li>
        </ul>
        <label id="note-topics-label" class="sr-only" for="`note-topics-list`">
          topics
        </label>
      </div>
    </b-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingNoteTopics',
  mixins: [Context, Util],
  props: {
    functionAdd: {
      type: Function,
      required: true
    },
    functionRemove: {
      type: Function,
      required: true
    },
    suggestedTopics: {
      type: Array,
      required: false
    },
    topics: {
      type: Array,
      required: true
    }
  },
  data: () => ({
    topic: undefined
  }),
  watch: {
    topic: function(newTopic, oldTopic) {
      if (newTopic && newTopic.indexOf(oldTopic, 0) !== -1) {
        this.debouncedSuggest();
      }
    }
  },
  created: function() {
    this.debouncedSuggest = this.debounce(this.suggest, 500);
  },
  methods: {
    addTopic() {
      if (this.topic && this.topic.trim()) {
        this.functionAdd(this.topic);
        this.alertScreenReader(`Topic ${this.topic} added.`);
        this.topic = undefined;
      }
    },
    normalizeString(str) {
      return str.toUpperCase().replace(/[^A-Z]/g, '');
    },
    removeTopic(topic) {
      this.functionRemove(topic);
      this.alertScreenReader(`Topic ${topic} removed.`);
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
</style>
