<template>
  <div v-if="loading" id="spinner-when-loading" class="spinner">
    <font-awesome icon="sync" size="5x" spin />
  </div>
</template>

<script>
import Context from '@/mixins/Context.vue';
import Loading from '@/mixins/Loading.vue';

export default {
  mixins: [Context, Loading],
  props: {
    alertPrefix: {
      type: String,
      default: 'The page'
    },
    isPlural: {
      type: Boolean
    }
  },
  watch: {
    loading(value) {
      this.alert(value, true);
    }
  },
  created() {
    this.alert(this.loading, false);
  },
  methods: {
    alert(isLoading, voiceIfLoaded)  {
      if (isLoading) {
        this.alertScreenReader(`${this.alertPrefix} ${this.isPlural ? 'are' : 'is'} loading...`);
      } else if (voiceIfLoaded) {
        this.alertScreenReader(`${this.alertPrefix} ${this.isPlural ? 'have' : 'has'} loaded.`);
      }
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
