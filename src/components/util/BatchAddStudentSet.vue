<template>
  <div>
    <div class="mb-2">
      <label
        :for="`batch-degree-check-${objectType}`"
        class="font-weight-700 input-label"
      ><span class="sr-only">Select a </span>{{ header }}</label>
    </div>
    <select
      :id="`batch-degree-check-${objectType}`"
      :aria-label="`Degree check will be created for all students in selected ${objectType}${objects.length === 1 ? '' : 's'}`"
      class="bordered-select d-block mb-2 ml-0 select-menu w-100"
      :disabled="disabled"
    >
      <option class="font-weight-black" selected :value="null">
        {{ objectType === 'cohort' ? 'Add Cohort' : 'Add Group' }}
      </option>
      <option
        v-for="object in objects"
        :id="`batch-degree-check-${objectType}-option-${object.id}`"
        :key="object.id"
        :aria-label="`Add ${objectType} ${object.name}`"
        class="truncate-with-ellipsis"
        :disabled="includes(addedIds, object.id)"
        @click="add(object)"
      >
        {{ object.name }}
      </option>
    </select>
    <div>
      <div v-for="(addedObject, index) in added" :key="addedObject.id" class="mb-1">
        <span class="font-weight-700 pill pill-attachment pl-2 text-uppercase text-no-wrap">
          <span :id="`batch-degree-check-${objectType}-${index}`">{{ truncate(addedObject.name) }}</span>
          <v-btn
            :id="`remove-${objectType}-from-batch-${index}`"
            class="pa-0"
            :disabled="disabled"
            variant="plain"
            @click.prevent="remove(addedObject)"
          >
            <v-icon
              :icon="mdiCloseCircleOutline"
              class="font-size-20 pl-2"
              color="error"
            />
            <span class="sr-only">Remove</span>
          </v-btn>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {mdiCloseCircleOutline} from '@mdi/js'
import {computed, ref} from 'vue'
import {filter as _filter, includes, map, truncate} from 'lodash'

const props = defineProps({
  addObject: {
    required: true,
    type: Function
  },
  disabled: {
    required: false,
    type: Boolean
  },
  header: {
    required: true,
    type: String
  },
  objects: {
    required: true,
    type: Array
  },
  objectType: {
    required: true,
    type: String
  },
  removeObject: {
    required: true,
    type: Function
  }
})

const added = ref([])
const addedIds = computed(() => map(added.value, 'id'))

const add = object => {
  added.value.push(object)
  props.addObject(object)
  alertScreenReader(`${props.header} '${object.name}' added to batch`)
}

const remove = object => {
  added.value = _filter(added.value, a => a.id !== object.id)
  props.removeObject(object)
  alertScreenReader(`${props.header} '${object.name}' removed`)
  putFocusNextTick(`batch-degree-check-${props.objectType}`, 'button')
}
</script>

<style scoped>
.bordered-select {
  border: 1px solid #000;
}
</style>
