<template>
  <div v-if="loading" id="spinner-when-loading" class="spinner">
    <v-progress-circular
      class="spinner"
      :size="50"
      color="primary"
      indeterminate
    />
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
