<template>
  <div class="py-1 d-flex flex-column">
    <label
      :for="`batch-note-${type}`"
      class="font-size-16 font-weight-bold"
    >
      <span class="sr-only">Select a </span>{{ isCuratedGroupsMode ? 'Curated Group' : 'Cohort' }}
    </label>
    <select
      :id="`batch-note-${type}`"
      v-model="model"
      :aria-label="`Note will be created for all students in selected ${type}${options.length === 1 ? '' : 's'}`"
      class="select-menu mt-1 w-75"
      :class="{'w-100': $vuetify.display.smAndDown}"
      :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
      autocomplete="off"
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
        :disabled="!!find(selectedOptions, ['id', option.id])"
        :value="option"
      >
        {{ option.name }}
      </option>
    </select>
    <ul v-if="size(selectedOptions)" :aria-label="isCuratedGroupsMode ? 'Curated Groups' : 'Cohorts'" class="list-no-bullets mt-2">
      <li v-for="selectedOption in selectedOptions" :key="selectedOption.id">
        <PillItem
          :id="`batch-note-${type}-${selectedOption.id}`"
          class="my-1 w-fit-content"
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
import {find, size} from 'lodash'
import {ref} from 'vue'
import PillItem from '@/components/util/PillItem'
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
