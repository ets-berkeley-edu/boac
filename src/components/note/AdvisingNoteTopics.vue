<template>
  <div v-if="size(topicOptions)">
    <label id="add-note-topic-label" class="font-weight-bold" for="add-note-topic">
      Topic Categories
    </label>
    <div class="pt-3">
      <select
        id="add-topic-select-list"
        :key="topicOptions.length"
        v-model="selected"
        aria-label="Use up and down arrows to review topics. Hit enter to select a topic."
        class="select-menu"
        :disabled="disabled"
        @change="onSelectChange"
      >
        <option :value="null" disabled>Select...</option>
        <option
          v-for="option in topicOptions"
          :key="option.value"
          :disabled="option.disabled"
          :value="option.value"
        >
          {{ option.text }}
        </option>
      </select>
    </div>
    <div>
      <ul
        id="note-topics-list"
        class="mb-2 pill-list pl-0"
        aria-labelledby="note-topics-label"
      >
        <li
          v-for="(topic, index) in selectedTopics"
          :id="`${noteId ? `note-${noteId}` : 'note'}-topic-${index}`"
          :key="index"
          class="list-item"
        >
          {{ topic }}
          <div class="float-right">
            <v-btn
              :id="`remove-${noteId ? `note-${noteId}` : 'note'}-topic-${index}`"
              :disabled="disabled"
              variant="text"
              class="remove-topic-btn"
              @click="() => remove(topic)"
            >
              <v-icon color="error" :icon="mdiCloseCircle" />
              <span class="sr-only">Remove</span>
            </v-btn>
          </div>
        </li>
      </ul>
      <label id="note-topics-label" class="sr-only" for="note-topics-list">
        topics
      </label>
    </div>
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {computed, ref, watch} from 'vue'
import {each, includes, size} from 'lodash'
import {getTopicsForNotes} from '@/api/topics'
import {mdiCloseCircle} from '@mdi/js'
import {useNoteStore} from '@/stores/note-edit-session/index'

const noteStore = useNoteStore()
const disabled = computed(() => noteStore.isSaving || noteStore.boaSessionExpired)
const noteId = ref(noteStore.model.topics)
const selected = ref(null)
const topicOptions = ref([])
const selectedTopics = ref(noteStore.model.topics)

watch(selected, async value => value && noteStore.addTopic(value))

getTopicsForNotes(false).then(rows => {
  each(rows, row => {
    const value = row['topic']
    const disabled = includes(selectedTopics.value, value)
    topicOptions.value.push({text: value, value, disabled})
  })
})

const remove = topic => {
  noteStore.removeTopic(topic)
  alertScreenReader(`Removed topic ${topic}.`)
  putFocusNextTick('add-topic-select-list')
}

const onSelectChange = () => {
  if (selected.value) {
    putFocusNextTick('add-topic-select-list')
    alertScreenReader(`Topic ${selected.value} added.`)
    selected.value = null
  }
}
</script>

<style scoped>
.list-item {
  background-color: #fff;
  border-radius: 5px;
  border: 1px solid #999;
  color: #666;
  display: inline-block;
  height: 36px;
  margin-top: 6px;
  padding: 5px 0 0 8px;
  min-width: 50%;
}
.remove-topic-btn {
  padding: 0 0 10px 0 !important;
  margin-right: -10px;
}
.select-menu {
  -moz-appearance: none;
  -webkit-appearance: none;
  appearance: none;
  border-radius: .25rem;
  border: 1px solid #ced4da;
  color: #495057;
  display: inline-block;
  font-size: 1rem;
  font-weight: 400;
  height: calc(1.5em + .75rem + 2px);
  line-height: 1.5;
  padding: .375rem 1.75rem .375rem .75rem;
  vertical-align: middle;
}
</style>
