<template>
  <v-app class="background-blue-sky vh-100">
    <v-main class="align-center d-flex flex-column">
      <div class="logo-container">
        <div class="stripe" />
        <div class="airplane-container">
          <img src="@/assets/airplane.svg" alt="Airplane logo" class="airplane" />
        </div>
      </div>
      <v-card class="card" rounded="0">
        <v-card-title class="card-title pb-0">
          <h1 id="page-header">BOA</h1>
        </v-card-title>
        <v-card-text class="pa-0 text-center">
          <v-btn
            id="sign-in"
            class="sign-in"
            color="primary"
            @click.stop="logIn"
          >
            Sign In
          </v-btn>
          <div v-if="config.devAuthEnabled" class="mt-3">
            <DevAuth :report-error="reportError" />
          </div>
          <div class="error-message font-size-14 text-error">
            {{ error }}
          </div>
          <div class="contact-us">
            If you have questions or feedback then contact us at
            <a :href="`mailto:${config.supportEmailAddress}`" target="_blank">
              {{ config.supportEmailAddress }}<span class="sr-only"> (link will open new browser tab)</span>
            </a>
          </div>
        </v-card-text>
      </v-card>
      <div class="copyright">&copy; {{ new Date().getFullYear() }} The Regents of the University of California</div>
    </v-main>
  </v-app>
</template>

<script setup>
import DevAuth from '@/components/admin/DevAuth'
import {getCasLoginURL} from '@/api/auth'
import {nextTick, ref} from 'vue'
import {trim} from 'lodash'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const config = useContextStore().config
const error = ref(undefined)
const route = useRoute()

nextTick(() => reportError(route.query.error))

const logIn = () => {
  getCasLoginURL().then(data => window.location.href = data.casLoginUrl)
}

const reportError = message => {
  error.value = trim(message) || null
}
</script>

<style scoped>
h1 {
  color: rgb(var(--v-theme-primary));
  font-weight: 200;
  font-size: 81px;
  letter-spacing: 8px;
  margin-bottom: 0;
  padding-top: 14px;
}
.airplane {
  background-color: rgb(var(--v-theme-on-primary));
  border: 10px solid rgb(var(--v-theme-primary));
  border-radius: 50px;
  object-fit: scale-down;
  width: 96px;
}
.airplane-container {
  left: 110px;
  position: absolute;
  top: 64px
}
.background-blue-sky {
  background: url('@/assets/blue-sky-background.jpg') no-repeat center center fixed;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
}
.card {
  opacity: 0.8;
  width: 320px;
}
.card-title {
  text-align: center;
}
.contact-us {
  margin: 0px 33px 12px 33px;
  text-align: left;
}
.copyright {
  background-color: rgb(var(--v-theme-primary));
  font-size: 12px;
  color: rgb(var(--v-theme-on-primary));
  height: 40px;
  padding-top: 10px;
  width: 320px;
  text-align: center;
  z-index: 1;
}
.error-message {
  color: rgb(var(--v-theme-error));
  font-weight: 500;
  min-height: 24px;
  margin: 10px 0 8px 0;
}
.logo-container {
  padding-top: 106px;
  position: relative;
  width: 320px;
  z-index: 1;
}
.sign-in {
  font-size: 20px;
  height: 50px;
  width: 264px;
  text-transform: capitalize;
  z-index: 1;
}
.stripe {
  background-color: rgb(var(--v-theme-primary));
  height: 10px;
  max-height: 10px !important;
  position:relative;
  width: 320px;
  max-width: 320px !important;
}
</style>
