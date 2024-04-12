<template>
  <div>
    <span
      v-if="get(standing, 'status') && standing.status !== 'GST'"
      :id="`${rowIndex ? rowIndex + '-' : ''}academic-standing-term-${termId}`"
      class="text-error font-weight-bold mb-1"
    >
      {{ standingStatus }} <span class="text-no-wrap">({{ termName }})</span>
    </span>
  </div>
</template>

<script setup>
import {get} from 'lodash'
import {useContextStore} from '@/stores/context'
</script>

<script>
import {sisIdForTermName, termNameForSisId} from '@/berkeley'

export default {
  name: 'StudentAcademicStanding',
  props: {
    rowIndex: {
      default: undefined,
      required: false,
      type: String
    },
    standing: {
      required: true,
      type: Object
    }
  },
  computed: {
    standingStatus() {
      return get(useContextStore().config, `academicStandingDescriptions.${this.standing.status}`, this.standing.status)
    },
    termId() {
      return this.standing.termId || sisIdForTermName(this.standing.termName)
    },
    termName() {
      return this.standing.termName || termNameForSisId(this.standing.termId)
    }
  }
}
</script>
