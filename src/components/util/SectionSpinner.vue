<template>
  <div v-if="loading" class="spinner">
    <v-progress-circular
      color="primary"
      indeterminate
      :size="size"
    />
  </div>
</template>

<script setup>
defineProps({
  loading: {
    required: true,
    type: Boolean
  },
  size: {
    type: Number,
    default: 30
  }
})
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
