<template>
  <div v-if="announcement && announcement.isPublished">
    <div
      v-if="!dismissedServiceAnnouncement"
      class="d-inline-block pt-3 pb-0 px-3 service-announcement w-100"
    >
      <div class="sr-only" role="heading">BOA Service Alert</div>
      <span
        id="service-announcement-banner"
        aria-live="polite"
        role="alert"
        v-html="announcement.text"
      >
      </span>
    </div>
    <div class="sr-only">
      <b-button id="toggle-service-announcement" @click="toggle">
        {{ dismissedServiceAnnouncement ? 'Restore' : 'Dismiss' }} BOA service alert
      </b-button>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

export default {
  name: 'ServiceAnnouncement',
  mixins: [Context, Util],
  methods: {
    toggle() {
      if (this.dismissedServiceAnnouncement) {
        this.restoreServiceAnnouncement()
        this.alertScreenReader('Alert restored')
        this.putFocusNextTick('service-announcement-banner')
      } else {
        this.dismissServiceAnnouncement()
        this.alertScreenReader('Dismissed')
        this.putFocusNextTick('toggle-service-announcement')
      }
    },

  }
}
</script>
