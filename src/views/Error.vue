<template>
  <div class="default-margins">
    <h1 id="page-header">{{ title }}</h1>
    <div
      id="error-message"
      aria-live="polite"
      class="text-medium-emphasis mt-3"
      role="alert"
    >
      <div v-html="message" />
      <div v-if="!config.isProduction && errorStatus" class="mt-3">
        HTTP error status: {{ errorStatus }}
      </div>
    </div>
  </div>
</template>

<script setup>
import {capitalize} from 'lodash'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()
const config = contextStore.config
const route = useRoute()

const errorStatus = route.query.s
const message = route.query.m || 'Uh oh, there was a problem.'
const title = route.query.t ? `Error: ${capitalize(route.query.t)}` : 'Error'
</script>
