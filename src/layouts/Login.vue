<template>
  <div>
    Hello World
  </div>
</template>

<script>
import Util from '@/mixins/Util'
import {getCasLoginURL} from '@/api/auth'

export default {
  name: 'Login',
  mixins: [Util],
  data: () => ({
    error: undefined,
    showError: false
  }),
  created() {
    this.reportError(this.$route.query.error)
  },
  methods: {
    logIn() {
      getCasLoginURL().then(data => window.location.href = data.casLoginUrl)
    },
    onHidden() {
      this.error = null
      this.showError = false
    },
    reportError(error) {
      error = this._trim(error)
      if (error.length) {
        this.error = error
        this.showError = true
      }
    }
  }
}
</script>
