<template>
  <div>
    <span
      v-if="get(standing, 'status') && standing.status !== 'GST'"
      :id="`${idPrefix}-academic-standing-term-${termId}`"
      class="text-error font-weight-bold"
      :class="{'demo-mode-blur': currentUser.inDemoMode}"
    >
      {{ standingStatus }} <span class="text-no-wrap">({{ standing.termName || termNameForSisId(standing.termId) }})</span>
    </span>
  </div>
</template>

<script lang="ts" setup>
import {get} from 'lodash'
import {sisIdForTermName, termNameForSisId} from '@/lib/berkeley-utils'
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

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const standingStatus = get(contextStore.config.academicStandingDescriptions, props.standing.status, props.standing.status)
const termId = props.standing.termId || sisIdForTermName(props.standing.termName)
</script>
