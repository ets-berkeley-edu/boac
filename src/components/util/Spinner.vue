<template>
  <div v-if="loading" id="spinner-when-loading" class="spinner">
    <font-awesome icon="sync" size="5x" spin />
  </div>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'Spinner',
  mixins: [Context],
}
</script>

<style scoped>
.spinner {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  height: 2em;
  margin: auto;
  overflow: show;
  width: 2em;
  z-index: 999;
}
</style>
