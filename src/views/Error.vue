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
      <div v-if="!config.isProduction" class="mt-3">
        <div v-if="errorStatus">
          HTTP error status: {{ errorStatus }}
        </div>
        <div v-if="errorClass">
          {{ errorClass }}
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {capitalize, toString} from 'lodash'
import {useRoute} from 'vue-router'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const config = contextStore.config
const route = useRoute()

const errorClass = toString(route.query.c).replace(/['<>]/g, '').replace('class ', '')
const errorStatus = route.query.s
const message = route.query.m || 'Uh oh, there was a problem.'
const title = route.query.t ? `Error: ${capitalize(toString(route.query.t))}` : 'Error'
</script>
