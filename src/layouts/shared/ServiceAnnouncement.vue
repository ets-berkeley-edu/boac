<template>
  <div v-if="announcement && announcement.isPublished">
    <div v-if="!dismissedServiceAnnouncement" class="align-top d-flex service-announcement">
      <div class="d-inline-block pb-0 pl-3 pr-1 pt-3 w-100">
        <div class="sr-only" role="heading">BOA Service Alert</div>
        <span
          id="service-announcement-banner"
          aria-live="polite"
          role="alert"
          v-html="announcement.text"
        >
        </span>
      </div>
      <div class="pr-1 pt-1">
        <b-btn
          id="dismiss-service-announcement"
          title="Dismiss"
          variant="link"
          @click="toggle"
        >
          <font-awesome icon="times" />
          <span class="sr-only">Dismiss alert</span>
        </b-btn>
      </div>
    </div>
    <b-btn v-if="dismissedServiceAnnouncement" id="restore-service-announcement" class="sr-only">Restore alert</b-btn>
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
        this.$announcer.polite('Alert restored')
        this.putFocusNextTick('service-announcement-banner')
      } else {
        this.dismissServiceAnnouncement()
        this.$announcer.polite('Dismissed')
        this.putFocusNextTick('toggle-service-announcement')
      }
    },

  }
}
</script>
