<template>
  <div>
    <label
      :id="`note-topics-label-${noteId}`"
      class="font-size-16 font-weight-bold"
      :class="labelClass"
      for="add-topic-select-list"
    >
      Topic {{ size(options) === 1 ? 'Category' : 'Categories' }}
    </label>
    <div v-if="!readOnly && size(options)" class="mb-1 mt-2">
      <select
        id="add-topic-select-list"
        :key="noteStore.model.topics.length"
        v-model="selected"
        autocomplete="off"
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
        :id="`note-topics-list-${noteId}`"
        class="advising-note-pill-list list-no-bullets mt-2"
        :aria-labelledby="`note-topics-label-${noteId}`"
      >
        <li
          v-for="(topic, index) in (note ? note.topics : noteStore.model.topics)"
          :id="`note-topics-list-item-${noteId}-${index}`"
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
            <span :class="{'demo-mode-blur': currentUser.inDemoMode}" class="truncate-with-ellipsis pr-1">
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
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  labelClass: {
    default: '',
    required: false,
    type: String
  },
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
const currentUser = useContextStore().currentUser
const disabled = computed(() => noteStore.isSaving || noteStore.boaSessionExpired)
const selected = ref(null)
const {xs} = useDisplay()

const noteId = computed(() => props.note ? props.note.id : noteStore.model.id)
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
