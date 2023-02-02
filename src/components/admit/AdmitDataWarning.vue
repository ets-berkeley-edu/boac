<template>
  <h2 v-if="show" class="font-size-16 has-error mb-0 py-1">
    <span class="has-error mr-1"><font-awesome icon="exclamation-triangle" /></span>
    Admit data was last updated on {{ $options.filters.moment(localUpdatedAt, 'MMM D, YYYY') }}
  </h2>
</template>

<script>
export default {
  name: 'AdmitDataWarning',
  props: {
    updatedAt: {
      type: String,
      required: false
    }
  },
  data: () => ({
    localUpdatedAt: undefined,
    show: undefined
  }),
  created() {
    const now = this.$moment()
    if (this.updatedAt) {
      this.localUpdatedAt = this.$moment(this.updatedAt).tz(this.$config.timezone)
      this.show = this.$moment.duration(now.diff(this.localUpdatedAt)).as('hours') >= 24
    }
  }
}
</script>
