<template>
  <div>
    <div v-if="loading" class="spinner">
      <font-awesome :size="`${faSize}x`" icon="sync" spin />
      <span
        role="alert"
        aria-live="polite"
        class="sr-only">Loading...</span>
    </div>
    <div v-if="!loading && !noAnnounce">
      <span
        v-if="name"
        role="alert"
        aria-live="polite"
        class="sr-only">
        <span>{{ name }} loaded</span>
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SectionSpinner',
  props: {
    noAnnounce: {
      type: Boolean
    },
    name: {
      type: String,
      default: undefined
    },
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
