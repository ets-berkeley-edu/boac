<template>
  <div>
    <label id="add-note-topic-label" class="font-size-16 font-weight-bold" for="add-topic-select-list">
      Topic Categories
    </label>
    <div v-if="!readOnly && size(topicOptions)" class="pt-2">
      <select
        id="add-topic-select-list"
        v-model="selected"
        aria-label="Use up and down arrows to review topics. Hit enter to select a topic."
        class="bg-white select-menu"
        :class="{'w-100': $vuetify.display.xs}"
        :disabled="disabled"
      >
        <option :value="null" disabled>Select...</option>
        <option
          v-for="option in topicOptions"
          :id="option.value"
          :key="option.value"
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
          v-for="(topic, index) in (topicsSelected)"
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

<script setup>
import {onMounted, ref, watch} from 'vue'
import {each, size} from 'lodash'
import PillItem from '@/components/util/PillItem'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {getTopicsForNotes} from '@/api/topics'

const props = defineProps({
  template: {
    default: () => {},
    required: false,
    type: Object
  },
  readOnly: {
    required: false,
    type: Boolean
  }
})

const emit = defineEmits(['update-topics'])
const disabled = ref(false)
const noteId = ref(props.template ? props.template.id : undefined)
const selected = ref(null)
const topicOptions = ref([])
const topicsSelected = ref([])

watch(selected => {
  if (selected.value) {
    topicsSelected.value.push(selected.value)
    alertScreenReader(`Added "${selected.value}" to topics.`)
    selected.value = null
  }
  putFocusNextTick('add-topic-select-list')
})

watch(topicsSelected, (newVal) => {
  emit('update-topics', newVal)
}, {deep: true})

onMounted(() => {
  if (!props.readOnly) {
    getTopicsForNotes(false).then(rows => {
      each(rows, row => {
        const value = row['topic']
        topicOptions.value.push({text: value, value, disabled})
      })
    })
  }
})

const remove = topic => {
  const index = topicsSelected.value.indexOf(topic)
  if (index !== -1) {
    topicsSelected.value.splice(index, 1)
  }

  alertScreenReader(`Removed "${topic}" from topics.`)
  putFocusNextTick('add-topic-select-list')
}
</script>


<style scoped>

</style>