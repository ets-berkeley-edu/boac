<template>
  <div>
    <div class="mb-2">
      <label
        :for="`batch-degree-check-${objectType}`"
        class="font-weight-bold input-label"
      ><span class="sr-only">Select a </span>{{ header }}</label>
    </div>
    <select
      :id="`batch-degree-check-${objectType}`"
      v-model="model"
      :aria-label="`Degree check will be created for all students in selected ${objectType}${objects.length === 1 ? '' : 's'}`"
      class="bordered-select d-block mb-2 ml-0 select-menu w-100"
      :disabled="disabled"
    >
      <option
        class="font-weight-black"
        :value="undefined"
      >
        {{ objectType === 'cohort' ? 'Add Cohort' : 'Add Group' }}
      </option>
      <option
        v-for="object in objects"
        :id="`batch-degree-check-${objectType}-option-${object.id}`"
        :key="object.id"
        :aria-label="`Add ${objectType} ${object.name}`"
        class="truncate-with-ellipsis"
        :disabled="includes(addedIds, object.id) || !object.totalStudentCount"
        :value="object"
      >
        {{ object.name }}&nbsp;&nbsp;({{ pluralize('student', object.totalStudentCount) }})
      </option>
    </select>
    <ul :id="`batch-degree-check-${objectType}-list`" class="mb-2 list-no-bullets pl-0 w-75">
      <li
        v-for="(addedObject, index) in added"
        :key="index"
        class="list-item"
      >
        <div class="d-flex justify-space-between">
          <div
            :id="`batch-degree-check-${objectType}-${index}`"
            class="truncate-with-ellipsis w-75"
          >
            {{ addedObject.name }}
          </div>
          <div class="float-right">
            <v-btn
              :id="`remove-${objectType}-from-batch-${index}`"
              class="remove-topic-btn"
              aria-label="Remove"
              color="error"
              :disabled="disabled"
              :icon="mdiCloseCircleOutline"
              variant="text"
              @click="() => remove(addedObject)"
            />
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import {alertScreenReader, pluralize, putFocusNextTick} from '@/lib/utils'
import {mdiCloseCircleOutline} from '@mdi/js'
import {computed, nextTick, ref, watch} from 'vue'
import {filter as _filter, includes, map} from 'lodash'

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
const model = ref(undefined)

watch(model, object => {
  if (object) {
    model.value = undefined
    nextTick(() => {
      added.value.push(object)
      props.addObject(object)
      alertScreenReader(`${props.header} '${object.name}' added to batch`)
    })
  }
})

const remove = object => {
  added.value = _filter(added.value, a => a.id !== object.id)
  props.removeObject(object)
  alertScreenReader(`${props.header} '${object.name}' removed`)
  putFocusNextTick(`batch-degree-check-${props.objectType}-list`, 'button')
}
</script>

<style scoped>
.bordered-select {
  border: 1px solid #000;
}
.list-item {
  background-color: #fff;
  border-radius: 5px;
  border: 1px solid #999;
  color: #666;
  height: 36px;
  margin-top: 6px;
  padding: 5px 0 0 8px;
  min-width: 50%;
}
.remove-topic-btn {
  padding: 0 0 10px 0 !important;
  margin-right: -10px;
}
</style>
