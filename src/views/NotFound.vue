<template>
  <span
    class="cloud-background ma-0 pa-0 h-100 w-100"
    aria-live="polite"
    role="alert"
    :style="{backgroundImage: `url(${cloudBackground})`, backgroundRepeat: 'repeat'}"
  >
    <span class="sr-only">Sorry, page not found. Contact us if the system is misbehaving.</span>
  </span>
  <div class="ticket-container text-center">
    <img
      alt="A silly boarding pass with the text, 'Error 404: Flight not found'"
      class="ticket-to-nowhere w-75"
      src="@/assets/boa-boarding-ticket.png"
    />
  </div>
</template>

<script setup>
import cloudBackground from '@/assets/404-cloud-background.jpg'
</script>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'NotFound',
  mixins: [Context],
  created() {
    this.loadingComplete('Page not found')
  }
}
</script>

<style scoped>
.cloud-background {
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  position: fixed;
  top:0;
  left:0;
  z-index: -1;
}
.ticket-container {
  min-height: 100vh;
  padding-top: 20%;
}
.ticket-to-nowhere {
  z-index: 999;
}
</style>
