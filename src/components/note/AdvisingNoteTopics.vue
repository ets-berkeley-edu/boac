<template>
  <div>
    <label id="add-note-topic-label" class="font-size-16 font-weight-bold" for="add-topic-select-list">
      Topic Categories
    </label>
    <div v-if="!readOnly && size(topicOptions)" class="mt-2">
      <select
        id="add-topic-select-list"
        :key="noteStore.model.topics.length"
        v-model="selected"
        aria-label="Use up and down arrows to review topics. Hit enter to select a topic."
        class="bg-white select-menu"
        :class="{'w-100': display.xs}"
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
        class="list-no-bullets mt-1 advising-note-pill-list"
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
import {computed, onMounted, ref, watch} from 'vue'
import {each, find, includes, size} from 'lodash'
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

const display = useDisplay()
const noteStore = useNoteStore()
const disabled = computed(() => noteStore.isSaving || noteStore.boaSessionExpired)
const noteId = ref(props.note ? props.note.id : noteStore.model.id)
const selected = ref(null)
const topicOptions = ref<SelectOption<string>[]>([])

watch(selected, value => {
  if (selected.value) {
    noteStore.addTopic(value)
    alertScreenReader(`Added "${selected.value}" to topics.`)
    selected.value = null
  }
  putFocusNextTick('add-topic-select-list')
})

onMounted(() => {
  each(props.topics, (topic: NoteTopic) => {
    topicOptions.value.push({
      disabled: includes(noteStore.model.topics, topic.topic),
      text: topic.topic,
      value: topic.topic
    })
  })
})

const remove = topic => {
  noteStore.removeTopic(topic)
  alertScreenReader(`Removed "${topic}" from topics.`)
  putFocusNextTick('add-topic-select-list')
}
</script>
