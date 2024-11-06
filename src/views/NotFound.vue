<template>
  <div class="boarding-pass-container d-flex text-center">
    <div class="my-auto">
      <v-slide-y-transition>
        <img
          v-show="showImage"
          alt="A silly boarding pass with the text, 'Error 404: Flight not found'"
          class="ticket-to-nowhere w-66"
          src="@/assets/boa-boarding-ticket.png"
        />
      </v-slide-y-transition>
    </div>
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
import {ref} from 'vue'

const showImage = ref(false)

setTimeout(
  () => {
    showImage.value = true
    alertScreenReader('Page not found')
  },
  200
)
</script>

<style scoped>
.boarding-pass-container {
  height: calc(100vh - 210px);
}
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
  opacity: 0.85;
}
</style>
