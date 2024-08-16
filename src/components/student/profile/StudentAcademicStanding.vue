<template>
  <div>
    <span
      v-if="get(standing, 'status') && standing.status !== 'GST'"
      :id="`${idPrefix}-academic-standing-term-${termId}`"
      class="text-error font-weight-bold"
    >
      {{ standingStatus }} <span class="text-no-wrap">({{ standing.termName || termNameForSisId(standing.termId) }})</span>
    </span>
  </div>
</template>

<script setup>
import {get} from 'lodash'
import {sisIdForTermName, termNameForSisId} from '@/berkeley'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  idPrefix: {
    required: true,
    type: String
  },
  standing: {
    required: true,
    type: Object
  }
})

const standingStatus = get(useContextStore().config, `academicStandingDescriptions.${props.standing.status}`, props.standing.status)
const termId = props.standing.termId || sisIdForTermName(props.standing.termName)
</script>
