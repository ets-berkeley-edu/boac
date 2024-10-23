<template>
  <router-link :to="{path, query}" @click="onClick">
    <slot></slot>
  </router-link>
</template>

<script setup>
import {computed} from 'vue'
import {useContextStore} from '@/stores/context'

const props = defineProps({
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

const contextStore = useContextStore()
const query = computed(() => {
  const args = props.queryArgs || {}
  return {
    ...{'_': contextStore.routeKeyId},
    ...args
  }
})

const onClick = () => {
  contextStore.setRouteKeyId(~contextStore.routeKeyId)
}
</script>
