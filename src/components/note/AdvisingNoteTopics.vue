<template>
  <div>
    <label id="add-note-topic-label" class="font-size-16 font-weight-bold text-medium-emphasis" for="add-topic-select-list">
      Topic {{ size(options) === 1 ? 'Category' : 'Categories' }}
    </label>
    <div v-if="!readOnly && size(options)" class="mb-1 mt-2">
      <select
        id="add-topic-select-list"
        :key="noteStore.model.topics.length"
        v-model="selected"
        aria-label="Use up and down arrows to review topics. Hit enter to select a topic."
        class="bg-white select-menu"
        :class="{'w-100': xs}"
        :disabled="disabled"
      >
        <option :value="null" disabled>Select...</option>
        <option
          v-for="option in options"
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
        class="advising-note-pill-list list-no-bullets mt-1"
        aria-labelledby="note-topics-label"
      >
        <li
          v-for="(topic, index) in (note ? note.topics : noteStore.model.topics)"
          :id="`note-topic-${index}`"
          :key="index"
        >
          <PillItem
            :id="`${noteId ? `note-${noteId}` : 'note'}-topic-${index}`"
            clazz="font-size-12 w-100"
            :closable="!readOnly"
            :disabled="disabled"
            :label="topic"
            name="topic"
            @close-clicked="remove(topic)"
          >
            <span class="truncate-with-ellipsis pr-1">
              {{ topic }}
            </span>
          </PillItem>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {computed, ref, watch} from 'vue'
import {find, includes, map, size} from 'lodash'
import {useDisplay} from 'vuetify'
import type {NoteTopic, SelectOption} from '@/lib/types'
import PillItem from '@/components/util/PillItem.vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  note: {
    default: undefined,
    required: false,
    type: Object
  },
  readOnly: {
    required: false,
    type: Boolean
  },
  topics: {
    default: () => [],
    required: false,
    type: Array as PropType<NoteTopic[]>
  }
})

const noteStore = useNoteStore()
const disabled = computed(() => noteStore.isSaving || noteStore.boaSessionExpired)
const noteId = ref(props.note ? props.note.id : noteStore.model.id)
const selected = ref(null)
const {xs} = useDisplay()

const options = computed<SelectOption<string>[]>(() => {
  return map(props.topics, (topic: NoteTopic) => ({
    disabled: includes(noteStore.model.topics, topic.topic),
    text: topic.topic,
    value: topic.topic
  }))
})

watch(selected, value => {
  if (selected.value) {
    noteStore.addTopic(value)
    alertScreenReader(`Added "${selected.value}" to topics.`)
    selected.value = null
  }
  putFocusNextTick('add-topic-select-list')
})

const remove = topic => {
  noteStore.removeTopic(topic)
  alertScreenReader(`Removed "${topic}" from topics.`)
  putFocusNextTick('add-topic-select-list')
}
</script>
