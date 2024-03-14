<template>
  <div>
    <label id="add-note-topic-label" class="font-weight-bold font-size-14" for="add-note-topic">
      Topic Categories
    </label>
    <v-select
      id="add-topic-select-list"
      v-model="selectedTopics"
      class="mt-2"
      density="compact"
      :disabled="disabled"
      hide-details
      item-title="text"
      :items="topicOptions"
      multiple
      persistent-hint
      return-object
      single-line
      variant="outlined"
      @update:model-value="onUpdate"
    >
      <template #item="{props}">
        <v-list-item
          v-bind="props"
          class="min-height-unset py-1"
          density="compact"
        >
        </v-list-item>
      </template>
      <template #selection="{item, index}">
        <v-chip
          :id="`${notePrefix}-topic-${index}`"
          class="v-chip-content-override font-weight-bold text-medium-emphasis text-uppercase text-nowrap"
          closable
          :close-label="`Remove ${item.title}`"
          density="comfortable"
          :disabled="disabled"
          variant="outlined"
          @click:close="onClickRemove(item.raw)"
          @keyup.enter="onClickRemove(item.raw)"
        >
          <span class="truncate-with-ellipsis">{{ item.title }}</span>
          <template #close>
            <v-icon color="error" :icon="mdiCloseCircle"></v-icon>
          </template>
        </v-chip>
      </template>
    </v-select>
  </div>
</template>

<script setup>
import {mdiCloseCircle} from '@mdi/js'
</script>

<script>
import {differenceBy, each, findIndex, includes, size} from 'lodash'
import {getTopicsForNotes} from '@/api/topics'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

export default {
  name: 'AdvisingNoteTopics',
  props: {
    noteId: {
      default: undefined,
      type: Number,
      required: false
    }
  },
  data: () => ({
    selectedTopics: [],
    topicOptions: []
  }),
  computed: {
    disabled() {
      return !!(useNoteStore().isSaving || useNoteStore().boaSessionExpired)
    },
    notePrefix() {
      return this.noteId ? `note-${this.noteId}` : 'note'
    }
  },
  created() {
    this.selectedTopics = useNoteStore().model.topics
    getTopicsForNotes(false).then(rows => {
      each(rows, row => {
        const topic = row['topic']
        this.topicOptions.push({
          text: topic,
          value: topic,
          disabled: includes(this.selectedTopics, topic)
        })
      })
    })
  },
  methods: {
    add(topic) {
      if (topic) {
        useNoteStore().addTopic(topic)
        putFocusNextTick('add-topic-select-list')
        useContextStore().alertScreenReader(`Topic ${topic} added.`)
      }
    },
    onClickRemove(topic) {
      const index = findIndex(this.selectedTopics, {'text': topic.text})
      this.selectedTopics.splice(index, 1)
      this.remove(topic)
    },
    onUpdate(selectedTopics) {
      const savedTopics = useNoteStore().model.topics
      const topic = differenceBy(selectedTopics, savedTopics)
      if (size(selectedTopics) > size(savedTopics)){
        this.add(topic.text)
      } else {
        this.remove(topic.text)
      }
    },
    remove(topic) {
      useNoteStore().removeTopic(topic.text)
      useContextStore().alertScreenReader(`Removed topic ${topic.text}.`)
      putFocusNextTick('add-topic-select-list')
    }
  }
}
</script>
