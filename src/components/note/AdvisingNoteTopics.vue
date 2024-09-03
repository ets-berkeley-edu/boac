<template>
  <div>
    <label id="add-note-topic-label" class="font-weight-bold" for="add-topic-select-list">
      Topic Categories
    </label>
    <div v-if="!readOnly && size(topicOptions)">
      <select
        id="add-topic-select-list"
        :key="noteStore.model.topics.length"
        v-model="selected"
        aria-label="Use up and down arrows to review topics. Hit enter to select a topic."
        class="bg-white select-menu"
        :class="{'w-100': $vuetify.display.xs}"
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
        class="list-no-bullets mt-1 topics-list"
        aria-labelledby="note-topics-label"
      >
        <li
          v-for="(topic, index) in (note ? note.topics : noteStore.model.topics)"
          :id="`note-topic-${index}`"
          :key="index"
        >
          <PillItem
            :id="`${noteId ? `note-${noteId}` : 'note'}-topic-${index}`"
            clazz="w-100"
            :closable="!readOnly"
            :disabled="disabled"
            :label="topic"
            name="topic"
            :on-click-close="() => remove(topic)"
          >
            <span class="truncate-with-ellipsis">
              {{ topic }}
            </span>
          </PillItem>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import PillItem from '@/components/util/PillItem'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {computed, ref, watch} from 'vue'
import {each, find, includes, size} from 'lodash'
import {getTopicsForNotes} from '@/api/topics'
import {useNoteStore} from '@/stores/note-edit-session/index'

const props = defineProps({
  note: {
    default: undefined,
    required: false,
    type: Object
  },
  readOnly: {
    required: false,
    type: Boolean
  }
})

const noteStore = useNoteStore()
const disabled = computed(() => noteStore.isSaving || noteStore.boaSessionExpired)
const noteId = ref(props.note ? props.note.id : noteStore.model.id)
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

const init = () => {
  if (!props.readOnly) {
    getTopicsForNotes(false).then(rows => {
      each(rows, row => {
        const value = row['topic']
        const disabled = includes(noteStore.model.topics, value)
        topicOptions.value.push({text: value, value, disabled})
      })
    })
  }
}

const remove = topic => {
  noteStore.removeTopic(topic)
  alertScreenReader(`Removed topic ${topic}.`)
  putFocusNextTick('add-topic-select-list')
}

init()
</script>

<style scoped>
.topics-list {
  max-width: 450px;
  width: 100%;
}
</style>
