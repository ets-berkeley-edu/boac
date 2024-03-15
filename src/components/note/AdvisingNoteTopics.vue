<template>
  <div>
    <label id="add-note-topic-label" class="font-weight-bold font-size-14" for="add-note-topic">
      Topic Categories
    </label>
    <v-select
      id="add-topic-select-list"
      :model-value="selectedTopics"
      class="mt-2"
      density="compact"
      :disabled="disabled"
      hide-details
      :items="topicOptions"
      multiple
      persistent-hint
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
          :close-label="`Remove ${item}`"
          density="comfortable"
          :disabled="disabled"
          variant="outlined"
          @click:close="onClickRemove(item)"
          @keyup.enter="onClickRemove(item)"
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
import {differenceBy, each, size} from 'lodash'
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
    topicOptions: []
  }),
  computed: {
    disabled() {
      return !!(useNoteStore().isSaving || useNoteStore().boaSessionExpired)
    },
    notePrefix() {
      return this.noteId ? `note-${this.noteId}` : 'note'
    },
    selectedTopics: {
      get() {
        return useNoteStore().model.topics
      },
      set(topics) {
        const topicsToAdd = differenceBy(topics, useNoteStore().model.topics)
        const topicsToRemove = differenceBy(useNoteStore().model.topics, topics)
        if (size(topicsToAdd)) {
          this.add(topicsToAdd[0])
        } else if (size(topicsToRemove)) {
          this.remove(topicsToRemove[0])
        }
      }
    }
  },
  created() {
    getTopicsForNotes(false).then(rows => {
      each(rows, row => {
        this.topicOptions.push(row.topic)
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
      this.remove(topic)
    },
    onUpdate(topics) {
      this.selectedTopics = topics
    },
    remove(topic) {
      useNoteStore().removeTopic(topic)
      useContextStore().alertScreenReader(`Removed topic ${topic}.`)
      putFocusNextTick('add-topic-select-list')
    }
  }
}
</script>
