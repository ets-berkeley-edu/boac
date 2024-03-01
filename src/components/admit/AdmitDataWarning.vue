<template>
  <h2 v-if="show" class="font-size-16 has-error mb-0 py-1">
    <span class="has-error mr-1"><v-icon :icon="mdiAlertRhombus" /></span>
    Admit data was last updated on {{ moment(localUpdatedAt).format('MMM D, YYYY') }}
  </h2>
</template>

<script setup>
import {mdiAlertRhombus} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import moment from 'moment'

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
    const now = this.moment()
    if (this.updatedAt) {
      this.localUpdatedAt = moment(this.updatedAt).tz(this.config.timezone)
      this.show = moment.duration(now.diff(this.localUpdatedAt)).as('hours') >= 24
    }
  },
  methods: {
    moment
  }
}
</script>
