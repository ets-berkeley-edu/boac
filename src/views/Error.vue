<template>
  <div class="m-2 p-3">
    <Spinner />
    <div v-if="!loading">
      <h1 class="page-section-header">{{ title }}</h1>
      <div
        id="error-message"
        aria-live="polite"
        class="faint-text mt-3"
        role="alert"
      >
        <div v-html="message" />
        <div v-if="!config.isProduction && errorStatus" class="mt-3">
          HTTP error status: {{ errorStatus }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Spinner from '@/components/util/Spinner'
import store from '@/store'
import Util from '@/mixins/Util'

export default {
  name: 'Error',
  mixins: [Context, Util],
  components: {Spinner},
  data: () => ({
    errorStatus: undefined,
    message: undefined,
    title: undefined
  }),
  mounted() {
    this.errorStatus = this.$route.query.s
    this.message = this.$route.query.m || 'Uh oh, there was a problem.'
    this.title = this.$route.query.t ? `Error: ${this._capitalize(this.$route.query.t)}` : 'Error'
    store.dispatch('context/loadingComplete')
    this.$announcer.polite(this.title)
  }
}
</script>
