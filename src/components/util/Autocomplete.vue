<template>
  <v-autocomplete
    :id="id"
    bg-color="transparent"
    :clearable="!isFetching"
    color="black"
    base-color="black"
    density="compact"
    :disabled="disabled"
    hide-details
    hide-no-data
    :items="items"
    :label="placeholder"
    :menu-icon="null"
    variant="outlined"
    @update:focused="s => console.log(`@update:focused: ${s}`)"
    @update:menu="s => console.log(`@update:menu: ${s}`)"
    @update:search="onUpdateSearch"
    @update:modelValue="s => console.log(`@update:modelValue=${s}`)"
    @click:clear="() => items = []"
  >
    <template #append-inner>
      <v-progress-circular
        v-if="isFetching"
        color="pale-blue"
        indeterminate
        :size="16"
        :width="3"
      />
    </template>
  </v-autocomplete>
</template>

<script>
import {ref} from 'vue'
import {map} from 'lodash'

export default {
  props: {
    disabled: {
      required: false,
      type: Boolean
    },
    fetch: {
      required: true,
      type: Function
    },
    id: {
      required: true,
      type: String
    },
    optionLabelKey: {
      default: 'title',
      required: false,
      type: String
    },
    optionValueKey: {
      default: 'value',
      required: false,
      type: String
    },
    placeholder: {
      default: undefined,
      required: false,
      type: String
    },
    suggestWhen: {
      default: query => query && query.length > 1,
      required: false,
      type: Function
    }
  },
  setup(props) {
    let isFetching = ref(false)
    let items = ref([])
    const onUpdateSearch = args => {
      isFetching.value = true
      if (props.suggestWhen(args)) {
        const controller = new AbortController()
        props.fetch(args, 20, controller).then(results => {
          items.value = map(results, result => ({title: result.label, value: result.uid}))
          isFetching.value = false
        })
      }
    }
    return {
      isFetching,
      items,
      onUpdateSearch
    }
  }
}
</script>
