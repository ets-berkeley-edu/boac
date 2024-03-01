<template>
  <div v-if="loading" class="spinner">
    <v-progress-circular :size="faSize" />
  </div>
</template>

<script>
export default {
  name: 'SectionSpinner',
  props: {
    faSize: {
      type: Number,
      default: 3
    },
    loading: Boolean
  }
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
