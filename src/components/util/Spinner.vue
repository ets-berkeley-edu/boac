<template>
  <v-progress-circular
    v-if="loading"
    id="spinner-when-loading"
    class="spinner"
    :size="50"
    color="primary"
    indeterminate
  />
</template>

<script setup>
import {computed} from 'vue'
import {useContextStore} from '@/stores/context'

const loading = computed(() => useContextStore().loading)
</script>

<style scoped>
.spinner {
  bottom: 0;
  height: 2em;
  left: 0;
  margin: auto;
  overflow: visible;
  position: fixed;
  right: 0;
  top: 0;
  width: 2em;
  z-index: 999;
}
</style>
