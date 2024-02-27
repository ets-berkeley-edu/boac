<template>
  <div>
    <span
      class="cloud-background m-0 p-0 h-100 w-100"
      aria-live="polite"
      role="alert"
    ><span class="sr-only">Sorry, page not found. Contact us if the system is misbehaving.</span></span>
    <div class="ticket-container text-center">
      <img
        alt="A silly boarding pass with the text, 'Error 404: Flight not found'"
        class="ticket-to-nowhere w-75"
        src="@/assets/boa-boarding-ticket.png"
      />
    </div>
  </div>
</template>

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
  background: url('~@/assets/404-cloud-background.jpg') no-repeat center center;
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
  align-content: center;
  min-height: 100vh;
  padding-top: 10%;
}
.ticket-to-nowhere {
  z-index: 999;
}
</style>
