<template>
  <div>
    <div v-if="loading" id="spinner-when-loading" class="spinner">
      <font-awesome icon="sync" size="5x" spin />
      <span
        role="alert"
        aria-live="assertive"
        class="sr-only">Page is loading...</span>
    </div>
    <div v-if="!loading">
      <span
        role="alert"
        aria-live="assertive"
        class="sr-only">Page has loaded.</span>
    </div>
  </div>
</template>

<script>
import Loading from '@/mixins/Loading.vue';

export default {
  mixins: [Loading]
};
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
