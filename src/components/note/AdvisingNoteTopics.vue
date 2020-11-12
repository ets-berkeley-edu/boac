<template>
  <div>
    <div>
      <label id="add-note-topic-label" class="font-weight-bold mt-2" for="add-topic-select-list">
        Topic Categories<span class="sr-only"> Use up and down arrows to scroll. Hit enter to select topic.</span>
      </label>
    </div>
    <b-container class="pl-0 ml-0">
      <b-row class="pb-1">
        <b-col cols="9">
          <div class="dropdown">
            <b-dropdown
              v-if="topicOptions.length"
              id="add-topic-select-list"
              aria-labelledby="add-note-topic-label"
              block
              :disabled="disabled"
              no-caret
              toggle-class="dd-override"
              variant="link"
              @hidden="alertScreenReader('Topic menu closed')"
              @shown="alertScreenReader('Topic menu opened')"
            >
              <template slot="button-content">
                <div class="d-flex dropdown-width justify-content-between text-dark">
                  <div>Select...</div>
                  <div class="ml-2">
                    <font-awesome icon="angle-down" class="menu-caret" />
                  </div>
                </div>
              </template>
              <b-dropdown-item-button
                v-for="(option, index) in topicOptions"
                :id="`add-topic-option-${option.value}`"
                :key="index"
                class="pl-3"
                :disabled="option.disabled"
                @click="add(option.value)"
                @keypress.enter="add(option.value)"
              >
                {{ option.text }}
              </b-dropdown-item-button>
            </b-dropdown>
          </div>
        </b-col>
      </b-row>
      <b-row>
        <ul
          id="note-topics-list"
          class="pill-list pl-3 pt-1"
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
                :aria-labelledby="`remove-${notePrefix}-topic-${index}-label`"
                variant="link"
                class="px-0 pt-1"
                tabindex="0"
                @click.prevent="remove(addedTopic)">
                <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
              </b-btn>
              <label :id="`remove-${notePrefix}-topic-${index}-label`" :for="`remove-${notePrefix}-topic-${index}`" class="sr-only">
                remove topic {{ topics[index] }}
              </label>
            </span>
          </li>
        </ul>
        <label id="note-topics-label" class="sr-only" for="note-topics-list">
          topics
        </label>
      </b-row>
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

<style scoped>
.dropdown {
  background-color: #fefefe;
  border: 1px solid #ccc;
  border-radius: 4px;
  color: #000;
  height: 42px;
  text-align: left;
  vertical-align: middle;
  white-space: nowrap;
}
</style>