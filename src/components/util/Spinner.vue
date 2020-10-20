<template>
  <div v-if="loading" id="spinner-when-loading" class="spinner">
    <font-awesome icon="sync" size="5x" spin />
  </div>
</template>

<script>
import Context from '@/mixins/Context.vue'
import Loading from '@/mixins/Loading.vue'

export default {
  mixins: [Context, Loading],
  props: {
    alertPrefix: {
      default: undefined,
      type: String
    },
    isPlural: {
      type: Boolean
    }
  },
  watch: {
    alertPrefix() {
      this.srAlert()
    },
    loading() {
      this.srAlert()
    }
  },
  data: () => ({
    alertHistory: []
  }),
  created() {
    this.srAlert()
  },
  methods: {
    srAlert() {
      if (this.alertPrefix) {
        const alert = this.loading ? `${this.alertPrefix} ${this.isPlural ? 'are' : 'is'} loading` : `${this.alertPrefix} loaded`
        const isRedundant = this.$_.includes(this.alertHistory, alert)
        if (!isRedundant) {
          this.alertScreenReader(alert)
          this.alertHistory.push(alert)
        }
      }
    }
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
