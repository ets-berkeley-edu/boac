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
              type="text"
              maxlength="255"
              list="add-topic-input-list"
              @keydown.enter="addTopic">
            </b-form-input>
            <b-form-datalist id="add-topic-input-list" :options="suggestedTopics"></b-form-datalist>
            <b-input-group-append>
              <b-button
                id="add-topic-button"
                slot="append"
                class="btn-add-topic"
                @click="addTopic">
                <i class="fas fa-plus pr-1"></i>Add
              </b-button>
            </b-input-group-append>
          </b-input-group>
        </b-col>
      </b-form-row>
      <div>
        <ul class="pill-list pl-0">
          <li
            v-for="(topic, index) in topics"
            :key="index">
            <span class="pill pill-attachment text-uppercase text-nowrap">
              {{ topic }}
              <b-btn
                :id="`remove-topic-${index}`"
                variant="link"
                class="px-0 pt-1"
                @click.prevent="functionRemove">
                <i class="fas fa-times-circle has-error pl-2"></i>
              </b-btn>
            </span>
          </li>
        </ul>
      </div>
    </b-container>
  </div>
</template>

<script>
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingNoteTopics',
  mixins: [Util],
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
      }
      this.topic = undefined;
    },
    normalizeString(str) {
      return str.toUpperCase().replace(/[^A-Z]/g, '');
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
