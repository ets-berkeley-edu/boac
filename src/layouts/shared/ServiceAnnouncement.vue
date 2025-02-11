<template>
  <div aria-live="assertive" role="alert">
    <div
      v-if="!contextStore.loading && announcement && announcement.isPublished"
      ref="serviceAlert"
    >
      <div v-if="!dismissedServiceAnnouncement" class="align-center bg-service-announcement d-flex font-weight-medium py-4 px-6">
        <div class="d-inline-block pr-1 service-announcement-container w-100">
          <span id="service-announcement-banner" v-html="announcement.text" />
        </div>
        <v-btn
          id="dismiss-service-announcement"
          color="transparent"
          elevation="0"
          :icon="mdiClose"
          size="x-small"
          title="Dismiss BOA Service Alert"
          @click="toggle"
        />
      </div>
    </div>
  </div>
  <v-btn
    v-if="!contextStore.loading && announcement && announcement.isPublished && dismissedServiceAnnouncement"
    id="restore-service-announcement"
    class="sr-only"
    @click="toggle"
  >
    Restore BOA Service Alert
  </v-btn>
</template>

<script setup>
import {mdiClose} from '@mdi/js'
import {useTemplateRef} from 'vue'
import {storeToRefs} from 'pinia'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const {announcement, dismissedServiceAnnouncement} = storeToRefs(contextStore)
const serviceAlertRef = useTemplateRef('serviceAlert')

defineExpose({ref: serviceAlertRef})

const toggle = () => {
  if (dismissedServiceAnnouncement.value) {
    contextStore.restoreServiceAnnouncement()
    putFocusNextTick('dismiss-service-announcement', {scroll: false})
  } else {
    contextStore.dismissServiceAnnouncement()
    putFocusNextTick('restore-service-announcement', {scroll: false})
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
