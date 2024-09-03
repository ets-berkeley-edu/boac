<template>
  <div class="py-1">
    <div>
      <label
        :for="`batch-note-${type}`"
        class="font-size-14 font-weight-bold"
      >
        <span class="sr-only">Select a </span>{{ header }}
      </label>
    </div>
    <select
      :id="`batch-note-${type}`"
      v-model="selected"
      :aria-label="`Note will be created for all students in selected ${type}${objects.length === 1 ? '' : 's'}`"
      class="select-menu mt-1"
      :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
      style="min-width: 50%"
    >
      <option
        :id="`batch-note-${type}-option-null`"
        :value="null"
      >
        Select...
      </option>
      <option
        v-for="object in objects"
        :id="`batch-note-${type}-option-${object.id}`"
        :key="object.id"
        :aria-label="`Add ${type} ${object.name}`"
        :disabled="!!find(added, ['id', object.id])"
        :value="object"
      >
        {{ object.name }}
      </option>
    </select>
    <ul class="list-no-bullets mt-1">
      <li v-for="object in added" :key="object.id">
        <PillItem
          :id="`batch-note-${type}-${object.id}`"
          closable
          :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
          :label="object.name"
          :name="type"
          :on-click-close="() => remove(object)"
        >
          <div class="truncate-with-ellipsis">{{ object.name }}</div>
        </PillItem>
      </li>
    </ul>
  </div>
</template>

<script setup>
import PillItem from '@/components/util/PillItem'
import {find, findIndex} from 'lodash'
import {ref, watch} from 'vue'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  objects: {
    required: true,
    type: Array
  },
  isCuratedGroupsMode: {
    required: true,
    type: Boolean
  },
  removeObject: {
    required: true,
    type: Function
  },
  update: {
    required: true,
    type: Function
  }
})

const noteStore = useNoteStore()
const added = ref([])
const header = props.isCuratedGroupsMode ? 'Curated Group' : 'Cohort'
const selected = ref(null)
const type = props.isCuratedGroupsMode ? 'curated' : 'cohort'

watch(selected, value => {
  if (value) {
    added.value.push(selected.value)
    props.update(added.value)
    selected.value = null
  }
})

const remove = object => {
  const index = findIndex(added.value, {'id': object.id})
  added.value.splice(index, 1)
  props.removeObject(object)
}
</script>
