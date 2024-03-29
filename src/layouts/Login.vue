<template>
  <div class="background-blue-sky font-size-14 vh-100">
    <div class="container w-100 px-4 mx-auto">
      <div class="stripe"></div>
      <div class="avatar-container">
        <img src="@/assets/airplane.svg" alt="Airplane logo" class="avatar-airplane" />
      </div>
      <div class="sign-in" role="main">
        <v-tooltip
          id="login-tooltip"
          v-model="showError"
          location="top"
          open-on-focus
          offset="5"
          @update:model-value="onHidden"
        >
          <template #activator="{ props }">
            <v-btn
              id="sign-in"
              v-bind="props"
              class="btn-sign-in"
              color="primary"
              @click.stop="logIn"
            >
              Sign In
            </v-btn>
          </template>
          <span
            class="has-error"
            aria-live="polite"
            v-html="error"
          ></span>
        </v-tooltip>
        <div class="contact-us">
          Questions or feedback? Contact us at
          <a
            :href="`mailto:${config.supportEmailAddress}`"
            target="_blank"
          >{{ config.supportEmailAddress }}<span class="sr-only"> (link will open new browser tab)</span></a>
        </div>
        <DevAuth v-if="config.devAuthEnabled" :report-error="reportError" />
      </div>
      <div class="box-container" role="banner">
        <div class="header">
          <h1>BOA</h1>
        </div>
      </div>
      <div class="copyright pt-2" role="contentinfo">
        <span class="font-size-12 text-white">&copy; {{ new Date().getFullYear() }} The Regents of the University of California</span>
      </div>
    </div>
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
    this.nextTick(() => this.reportError(this.$route.query.error))
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

<style scoped>
.avatar-airplane {
  background-color: #fff;
  border: 10px solid #0275d8;
  border-radius: 50px;
  object-fit: scale-down;
  width: 96px;
}
.avatar-container {
  align-items: center;
  display: flex;
  flex: 0 0 100px;
  position: absolute;
  top: 205px;
  left: 50%;
  transform: translate(-50%, -50%);
}
.background-blue-sky {
  background: url('@/assets/blue-sky-background.jpg') no-repeat center center
    fixed;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
}
.btn-sign-in {
  height: 50px;
  width: 256px;
  font-size: 20px;
  text-transform: capitalize;
}
.box-container {
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.5);
  flex: 1;
  height: 360px;
  min-height: 360px;
  width: 320px;
  opacity: 0.8;
  padding: 0 25px 0 25px;
  z-index: -1;
}
.contact-us {
  font-weight: 400;
  padding: 20px 40px 10px 40px;
  width: 320px;
  text-align: left;
}
.container {
  align-items: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 24em;
  padding-top: 200px;
  position: relative;
  z-index: 999;
}
.copyright {
  background-color: #3b80bf;
  height: 40px;
  width: 320px;
  padding-top: 10px;
  text-align: center;
  white-space: nowrap;
}
.header {
  padding-top: 40px;
  text-align: center;
}
.sign-in {
  position: absolute;
  top: 460px;
  left: 50%;
  text-align: center;
  transform: translate(-50%, -50%);
}
.stripe {
  background-color: #0275d8;
  height: 10px;
  width: 320px;
}
h1 {
  color: #0275d8;
  font-weight: 200;
  font-size: 81px;
  letter-spacing: 8px;
  padding-top: 14px;
}
</style>
