<template>
  <div class="py-1">
    <div>
      <label
        :for="`batch-note-${type}`"
        class="font-size-14 font-weight-bold"
      >
        <span class="sr-only">Select a </span>{{ isCuratedGroupsMode ? 'Curated Group' : 'Cohort' }}
      </label>
    </div>
    <select
      :id="`batch-note-${type}`"
      v-model="model"
      :aria-label="`Note will be created for all students in selected ${type}${options.length === 1 ? '' : 's'}`"
      class="select-menu mt-1 w-75"
      :class="{'w-100': $vuetify.display.smAndDown}"
      :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
      @change="onSelect"
    >
      <option
        :id="`batch-note-${type}-option-null`"
        :value="undefined"
      >
        Select...
      </option>
      <option
        v-for="option in options"
        :id="`batch-note-${type}-option-${option.id}`"
        :key="option.id"
        :aria-label="`Add ${type} ${option.name}`"
        :disabled="!!find(selectedOptions, ['id', option.id])"
        :value="option"
      >
        {{ option.name }}
      </option>
    </select>
    <ul class="list-no-bullets mt-1">
      <li v-for="selectedOption in selectedOptions" :key="selectedOption.id">
        <PillItem
          :id="`batch-note-${type}-${selectedOption.id}`"
          closable
          :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
          :label="selectedOption.name"
          :name="type"
          @close-clicked="remove(selectedOption)"
        >
          <div class="truncate-with-ellipsis">{{ selectedOption.name }}</div>
        </PillItem>
      </li>
    </ul>
  </div>
</template>

<script setup>
import PillItem from '@/components/util/PillItem'
import {find} from 'lodash'
import {ref} from 'vue'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  add: {
    required: true,
    type: Function
  },
  isCuratedGroupsMode: {
    required: true,
    type: Boolean
  },
  options: {
    required: true,
    type: Array
  },
  remove: {
    required: true,
    type: Function
  },
  selectedOptions: {
    required: true,
    type: Array
  }
})

const noteStore = useNoteStore()
const model = ref(undefined)
const type = props.isCuratedGroupsMode ? 'curated' : 'cohort'

const onSelect = () => {
  if (model.value) {
    props.add(model.value)
    model.value = undefined
  }
}
</script>
