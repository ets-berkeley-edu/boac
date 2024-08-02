<template>
  <div>
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
        @select="onChangeSelect"
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
        @select="onChangeSelect"
      >
        {{ object.name }}
      </option>
    </select>
    <div v-for="object in added" :key="object.id" class="ml-2 mt-2">
      <v-chip
        :id="`batch-note-${type}-${object.id}`"
        class="v-chip-content-override text-uppercase text-no-wrap"
        density="compact"
        variant="outlined"
      >
        <div class="truncate-with-ellipsis">{{ object.name }}</div>
        <template #close>
          <v-btn
            :id="`batch-note-remove-${type}-${object.id}`"
            :aria-label="`Remove ${type} ${object.name}`"
            color="error"
            exact
            :icon="mdiCloseCircle"
            variant="text"
            @click.stop="() => remove(object)"
            @keyup.enter.stop="() => remove(object)"
          />
        </template>
      </v-chip>
    </div>
  </div>
</template>

<script setup>
import {find, findIndex} from 'lodash'
import {mdiCloseCircle} from '@mdi/js'
import {ref} from 'vue'
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

const onChangeSelect = () => {
  added.value.push(selected.value)
  props.update(added.value)
  selected.value = null
}

const remove = object => {
  const index = findIndex(added.value, {'id': object.id})
  added.value.splice(index, 1)
  props.removeObject(object)
}
</script>
