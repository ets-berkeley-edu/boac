<template>
  <router-link :to="{path, query}" @click="() => counter++">
    <slot></slot>
  </router-link>
</template>

<script setup>
import {computed, ref} from 'vue'

const props = defineProps({
  defaultCounter: {
    type: Number,
    required: false,
    default: 0
  },
  path: {
    type: String,
    required: true
  },
  queryArgs: {
    default: undefined,
    required: false,
    type: Object
  }
})

const counter = ref(props.defaultCounter)
const query = computed(() => {
  const args = props.queryArgs || {}
  return {
    ...{'_': counter},
    ...args
  }
})
</script>
