<template>
  <div class="align-center d-flex h-100 justify-center">
    <img
      alt="A silly boarding pass with the text, 'Error 404: Flight not found'"
      class="ticket-to-nowhere w-66"
      src="@/assets/boa-boarding-ticket.png"
    />
  </div>
  <span
    class="cloud-background ma-0 pa-0 h-100 w-100"
    aria-live="polite"
    role="alert"
    :style="{backgroundImage: `url(${cloudBackground})`, backgroundRepeat: 'repeat'}"
  >
    <span class="sr-only">Sorry, page not found. Contact us if the system is misbehaving.</span>
  </span>
</template>

<script setup>
import cloudBackground from '@/assets/404-cloud-background.jpg'
import {alertScreenReader} from '@/lib/utils'

alertScreenReader('Page not found')
</script>

<style scoped>
.cloud-background {
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  left: 0;
  opacity: 0.7;
  position: fixed;
  top:0;
  z-index: -1;
}
.ticket-to-nowhere {
  opacity: 0.7;
}
</style>
