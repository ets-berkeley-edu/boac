<template>
  <div
    v-if="announcement && announcement.isPublished"
    style="display: inline-block"
    class="service-announcement pl-3 pt-3 pr-3 pb-0 w-100">
    <span
      id="service-announcement-banner"
      aria-live="polite"
      role="alert"
      v-html="announcement.text">
    </span>
  </div>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'ServiceAnnouncement',
  mixins: [Context]
}
</script>
