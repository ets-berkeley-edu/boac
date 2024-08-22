<template>
  <div v-if="size(topicOptions)">
    <label id="add-note-topic-label" class="font-weight-bold" for="add-topic-select-list">
      Topic Categories
    </label>
    <div class="mt-1">
      <select
        id="add-topic-select-list"
        :key="noteStore.model.topics.length"
        v-model="selected"
        aria-label="Use up and down arrows to review topics. Hit enter to select a topic."
        class="bg-white select-menu"
        :disabled="disabled"
      >
        <option :value="null" disabled>Select...</option>
        <option
          v-for="option in topicOptions"
          :key="option.value"
          :disabled="!!find(noteStore.model.topics, value => value === option.value)"
          :value="option.value"
        >
          {{ option.text }}
        </option>
      </select>
    </div>
    <div>
      <ul
        id="note-topics-list"
        :key="noteStore.model.topics.length"
        class="mb-2 pill-list pl-0 w-50"
        aria-labelledby="note-topics-label"
      >
        <li
          v-for="(topic, index) in noteStore.model.topics"
          :id="`note-topic-${index}`"
          :key="index"
          class="list-item"
        >
          <div class="d-flex justify-space-between">
            <div class="truncate-with-ellipsis w-75">
              {{ topic }}
            </div>
            <div class="float-right">
              <v-btn
                :id="`remove-${noteId ? `note-${noteId}` : 'note'}-topic-${index}`"
                :disabled="disabled"
                class="remove-topic-btn"
                variant="text"
                @click="() => remove(topic)"
              >
                <v-icon color="error" :icon="mdiCloseCircle" />
                <span class="sr-only">Remove</span>
              </v-btn>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {computed, ref, watch} from 'vue'
import {each, find, includes, size} from 'lodash'
import {getTopicsForNotes} from '@/api/topics'
import {mdiCloseCircle} from '@mdi/js'
import {useNoteStore} from '@/stores/note-edit-session/index'

const noteStore = useNoteStore()
const disabled = computed(() => noteStore.isSaving || noteStore.boaSessionExpired)
const noteId = ref(noteStore.model.id)
const selected = ref(null)
const topicOptions = ref([])

watch(selected, value => {
  if (selected.value) {
    noteStore.addTopic(value)
    alertScreenReader(`Topic ${selected.value} added.`)
    selected.value = null
  }
  putFocusNextTick('add-topic-select-list')
})

getTopicsForNotes(false).then(rows => {
  each(rows, row => {
    const value = row['topic']
    const disabled = includes(noteStore.model.topics, value)
    topicOptions.value.push({text: value, value, disabled})
  })
})

const remove = topic => {
  noteStore.removeTopic(topic)
  alertScreenReader(`Removed topic ${topic}.`)
  putFocusNextTick('add-topic-select-list')
}
</script>

<style scoped>
.list-item {
  background-color: #fff;
  border-radius: 5px;
  border: 1px solid #999;
  color: #666;
  height: 36px;
  margin-top: 6px;
  padding: 5px 0 0 8px;
  min-width: 50%;
}
.remove-topic-btn {
  padding: 0 0 10px 0 !important;
  margin-right: -10px;
}
</style>
