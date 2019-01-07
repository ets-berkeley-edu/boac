<template>
  <div>
    <div class="loading-spinner-large"
         v-if="loading">
      <i class="fas fa-sync fa-spin"
         :class="`fa-${faSize}x`"></i>
      <span role="alert"
            aria-live="passive"
            class="sr-only">Loading...</span>
    </div>
    <div v-if="!loading">
      <span role="alert"
            aria-live="passive"
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
    name: {
      type: String,
      default: 'Page content'
    },
    faSize: {
      type: Number,
      default: 3
    },
    loading: Boolean
  }
};
</script>

<style scoped>
.loading-spinner-large {
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
