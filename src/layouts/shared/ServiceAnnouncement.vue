<template>
  <v-expand-transition>
    <div v-if="announcement && announcement.isPublished" aria-labelledby="service-announcement-label" role="alert">
      <div v-if="!dismissedServiceAnnouncement" class="align-center bg-service-announcement d-flex font-weight-medium py-4 px-6">
        <div class="d-inline-block pr-1 service-announcement-container w-100">
          <h2 id="service-announcement-label" class="sr-only">BOA Service Alert</h2>
          <span
            id="service-announcement-banner"
            aria-live="polite"
            role="alert"
            v-html="announcement.text"
          />
        </div>
        <v-btn
          id="dismiss-service-announcement"
          aria-label="Dismiss alert"
          color="transparent"
          elevation="0"
          :icon="mdiClose"
          size="x-small"
          title="Dismiss"
          @click="toggle"
        />
      </div>
      <v-btn v-if="dismissedServiceAnnouncement" id="restore-service-announcement" class="d-sr-only">Restore alert</v-btn>
    </div>
  </v-expand-transition>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {computed} from 'vue'
import {mdiClose} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const announcement = computed(() => contextStore.announcement)
const dismissedServiceAnnouncement = computed(() => contextStore.dismissedServiceAnnouncement)

const toggle = () => {
  if (dismissedServiceAnnouncement.value) {
    contextStore.restoreServiceAnnouncement()
    alertScreenReader('Alert restored')
    putFocusNextTick('service-announcement-banner')
  } else {
    contextStore.dismissServiceAnnouncement()
    dismissedServiceAnnouncement.value = false
    alertScreenReader('Dismissed')
    putFocusNextTick('toggle-service-announcement')
  }
}
</script>

<style>
#service-announcement-banner li {
  padding-right: 20px;
  overflow-wrap: break-word;
}
#service-announcement-banner ol {
  margin-left: 30px;
}
#service-announcement-banner p {
  padding-right: 20px;
  overflow-wrap: break-word;
}
#service-announcement-banner ul {
  margin-left: 30px;
}
</style>

<style scoped>
.service-announcement-container {
  width: 98% !important;
}
</style>
