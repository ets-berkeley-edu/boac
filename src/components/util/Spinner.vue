<template>
  <div>
    <div id="spinner-when-loading" v-if="loading" class="spinner">
      <font-awesome icon="sync" size="5x" spin />
    </div>
    <span
      role="alert"
      aria-live="assertive"
      class="sr-only">{{ screenReaderAlert }}</span>
  </div>
</template>

<script>
import Loading from '@/mixins/Loading.vue';

export default {
  mixins: [Loading],
  props: {
    alertPrefix: {
      type: String,
      default: 'The page'
    },
    isPlural: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    screenReaderAlert() {
      return this.loading ? `${this.alertPrefix} ${this.isPlural ? 'are' : 'is'} loading...` : `${this.alertPrefix} ${this.isPlural ? 'have' : 'has'} loaded.`;
    }
  }
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
