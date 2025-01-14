<template>
  <v-row class="px-6 pt-10 pb-4">
    <v-col
      cols="5"
      lg="6"
      md="5"
      sm="3"
      xl="8"
    >
      <img alt="UC Berkeley logo" src="@/assets/uc-berkeley-logo.svg" />
    </v-col>
    <v-col
      class="font-size-14"
      cols="7"
      lg="6"
      md="7"
      sm="9"
      xl="4"
    >
      <div>
        Problem? Question? Suggestion?
        <a :href="`mailto:${supportEmailAddress}`" target="_blank">Email {{ supportEmailAddress }} <span class="sr-only"> (opens in new window)</span></a>
      </div>
      <div>
        &copy; {{ new Date().getFullYear() }} The Regents of the University of California
      </div>
    </v-col>
  </v-row>
</template>

<script setup>
import {useContextStore} from '@/stores/context'

const supportEmailAddress = useContextStore().config.supportEmailAddress
</script>

