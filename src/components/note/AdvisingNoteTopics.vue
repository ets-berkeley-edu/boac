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
                :disabled="disabled"
                variant="link"
                class="px-0 pt-1"
                @click.prevent="remove(addedTopic)">
                <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
                <span class="sr-only">Remove</span>
              </b-btn>
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
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import { getTopicsForNotes } from '@/api/topics'

export default {
  name: 'AdvisingNoteTopics',
  mixins: [Context, Util],
  props: {
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
    noteId: {
      default: undefined,
      type: Number,
      required: false
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
  computed: {
    notePrefix() {
      return this.noteId ? `note-${this.noteId}` : 'note'
    }
  },
  created() {
    getTopicsForNotes(false).then(rows => {
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
        this.putFocusNextTick('add-topic-select-list')
        this.alertScreenReader(`Topic ${topic} added.`)
      }
    },
    remove(topic) {
      this.setDisabled(topic, false)
      this.functionRemove(topic)
      this.alertScreenReader(`Removed topic ${topic}.`)
      this.putFocusNextTick('add-topic-select-list')
    },
    setDisabled(topic, disable) {
      const option = this.$_.find(this.topicOptions, ['value', topic])
      this.$_.set(option, 'disabled', disable)
    }
  }
}
</script>
