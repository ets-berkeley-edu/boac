<template>
  <div class="align-center d-flex">
    <v-autocomplete
      :id="id"
      v-model="selected"
      autocomplete="off"
      bg-color="transparent"
      :clearable="!isFetching"
      base-color="black"
      :class="{
        'demo-mode-blur': useContextStore().currentUser.inDemoMode,
        'autocomplete-with-add-button': !!onClickAddButton
      }"
      color="black"
      density="compact"
      :disabled="disabled"
      hide-details
      :hide-no-data="!showNoData"
      :items="items"
      :label="placeholder"
      :maxlength="maxlength"
      :menu-icon="null"
      variant="outlined"
      no-data-text="No Users Found"
      @click:clear="onClear"
      @update:menu="s => s ? null : $emit('user-selected', selected)"
      @update:search="onUpdateSearch"
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
    <v-btn
      v-if="onClickAddButton"
      :id="`${id}-add-button`"
      class="add-button"
      color="primary"
      variant="flat"
      @click="onClickAdd"
    >
      <v-icon :icon="mdiPlus" /> Add
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import {mdiPlus} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {find, map, noop} from 'lodash'
import {ref} from 'vue'
import _ from 'lodash'

const props = defineProps({
  ariaRequired: {
    required: false,
    type: Boolean
  },
  compact: {
    required: false,
    type: Boolean
  },
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
  onClickAddButton: {
    default: undefined,
    required: false,
    type: Function
  },
  onEsc: {
    default: noop,
    required: false,
    type: Function
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
  maxlength: {
    default: '56',
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
  },
  selection: {
    default: undefined,
    required: false,
    type: Object
  },
  showNoData: {
    required: false,
    type: Boolean
  }
})

let isFetching = ref(false)
let items = ref([])
let selected = ref(undefined)

const onClear = () => {
  items.value = []
  isFetching.value = false
}

const onClickAdd = () => {
  const item = find(items, [props.optionValueKey, selected])
  if (item) {
    if (props.onClickAddButton) {
      props.onClickAddButton(item)
      isFetching.value = false
    }
    // props.onClickAddButton(item)
    // isFetching.value = false
  }
}

const onUpdateSearch = _.debounce(args => {
  if (args?.length > 0) {
    isFetching.value = true
    if (props.suggestWhen(args)) {
      const controller = new AbortController()
      props.fetch(args, 20, controller).then(results => {
        items.value = map(results, result => ({title: result.label, value: result.uid}))
        isFetching.value = false
      })
    }
  } else {
    isFetching.value = false
  }
}, 500)

</script>

<style scoped>
.add-button {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
  height: 40px !important;
}
</style>
