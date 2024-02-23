<template>
  <div>
    Hello World
    <DevAuth v-if="config.devAuthEnabled" :report-error="reportError" />
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DevAuth from '@/components/admin/DevAuth'
import Util from '@/mixins/Util'
import {getCasLoginURL} from '@/api/auth'

export default {
  name: 'Login',
  components: {DevAuth},
  mixins: [Context, Util],
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
