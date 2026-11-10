<template>
  <v-row class="px-6 pt-10 pb-4">
    <v-col
      cols="5"
      lg="6"
      md="5"
      sm="3"
      xl="8"
    >
      <img alt="UC Berkeley" class="berkeley-logo" src="@/assets/uc-berkeley-logo.svg">
    </v-col>
    <v-col
      class="font-size-14"
      cols="7"
      lg="6"
      md="7"
      sm="9"
      xl="4"
    >
      <div class="float-right">
        <div>
          Problem? Question? Suggestion?
          <a :href="`mailto:${supportEmailAddress}`" target="_blank">Email {{ supportEmailAddress }} <span class="sr-only">&nbsp;(opens in new tab)</span></a>
        </div>
        <div>
          <a
            id="footer-accessibility-link"
            href="https://dap.berkeley.edu/get-help/report-web-accessibility-issue"
            target="_blank"
          >
            Accessibility<span class="sr-only">&nbsp;(opens in new tab)</span>
          </a>
        </div>
        <div>
          &copy; {{ new Date().getFullYear() }} The Regents of the University of California
        </div>
      </div>
    </v-col>
  </v-row>
</template>

<script setup>
import {useContextStore} from '@/stores/context'

const supportEmailAddress = useContextStore().config.supportEmailAddress
</script>

<style scoped>
/* The logo is text rendered as an image, so it is sized in rem (its native 117px wide at the default font
   size) to grow with the user's text size, per WCAG 1.4.4. max-width keeps it inside its column. */
.berkeley-logo {
  height: auto;
  max-width: 100%;
  width: 7.3125rem;
}
</style>

