<template>
  <div>
    <label id="add-note-topic-label" class="font-size-16 font-weight-700" for="add-note-topic">
      Topic Categories
    </label>
    <v-select
      v-if="topicOptions.length"
      id="add-topic-select-list"
      class="mt-2"
      density="compact"
      :disabled="disabled"
      hide-details
      :items="topicOptions"
      :model-value="selectedTopics"
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
        />
      </template>
      <template #selection="{item, index}">
        <v-chip
          :id="`${noteId ? `note-${noteId}` : 'note'}-topic-${index}`"
          class="v-chip-content-override font-weight-bold text-medium-emphasis text-uppercase text-no-wrap"
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
            <v-icon color="error" :icon="mdiCloseCircle" />
          </template>
        </v-chip>
      </template>
    </v-select>
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {computed} from 'vue'
import {differenceBy, each, size} from 'lodash'
import {getTopicsForNotes} from '@/api/topics'
import {mdiCloseCircle} from '@mdi/js'
import {useNoteStore} from '@/stores/note-edit-session'

defineProps({
  noteId: {
    default: undefined,
    type: Number,
    required: false
  }
})

const noteStore = useNoteStore()
const disabled = computed(() => noteStore.isSaving || noteStore.boaSessionExpired)
const topicOptions = []

getTopicsForNotes(false).then(rows => each(rows, row => topicOptions.push(row.topic)))

const add = topic => {
  if (topic) {
    noteStore.addTopic(topic)
    putFocusNextTick('add-topic-select-list')
    alertScreenReader(`Topic ${topic} added.`)
  }
}

const remove = topic => {
  noteStore.removeTopic(topic)
  alertScreenReader(`Removed topic ${topic}.`)
  putFocusNextTick('add-topic-select-list')
}

const onClickRemove = topic => remove(topic)

const selectedTopics = computed({
  get() {
    return noteStore.model.topics
  },
  set(topics) {
    const topicsToAdd = differenceBy(topics, noteStore.model.topics)
    const topicsToRemove = differenceBy(noteStore.model.topics, topics)
    if (size(topicsToAdd)) {
      add(topicsToAdd[0])
    } else if (size(topicsToRemove)) {
      remove(topicsToRemove[0])
    }
  }
})

const onUpdate = topics => selectedTopics.value = topics
</script>
