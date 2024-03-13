<template>
  <h2 v-if="show" class="font-size-16 has-error mb-0 py-1">
    <span class="has-error mr-1"><v-icon :icon="mdiAlertRhombus" /></span>
    Admit data was last updated on {{ DateTime.fromJSDate(localUpdatedAt).toFormat('MMM D, YYYY') }}
  </h2>
</template>

<script setup>
import {mdiAlertRhombus} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import {DateTime} from 'luxon'

export default {
  name: 'AdmitDataWarning',
  mixins: [Context],
  props: {
    updatedAt: {
      default: undefined,
      required: false,
      type: String
    }
  },
  data: () => ({
    localUpdatedAt: undefined,
    show: undefined
  }),
  created() {
    const now = DateTime.now()
    if (this.updatedAt) {
      this.localUpdatedAt = DateTime.fromObject(this.updatedAt).setZone(this.config.timezone)
      this.show = now.diff(this.localUpdatedAt, 'hours') >= 24
    }
  }
}
</script>
