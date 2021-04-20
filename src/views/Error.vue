<template>
  <div class="ml-4 mr-3 mt-4">
    <h1 class="page-section-header">Uh oh, we have an error.</h1>
    <div
      id="error-message"
      aria-live="polite"
      class="faint-text mt-3"
      role="alert"
      v-html="message || 'Uh oh, there was a problem.'"
    />
  </div>
</template>

<script>
import Loading from '@/mixins/Loading'

export default {
  name: 'Error',
  mixins: [Loading],
  data: () => ({
    message: undefined
  }),
  mounted() {
    this.message = this.$route.query.m
    this.loaded('Error')
  }
}
</script>
