<template>
  <div v-if="!termId || toInt(withdrawal.termId) === toInt(termId)">
    <span :id="`withdrawal-term-${termId}`" class="red-flag-status">
      {{ withdrawal.description }}
      ({{ withdrawal.reason }})
      <span class="text-nowrap">{{ moment(withdrawal.date).format('MMM DD, YYYY') }}</span>
    </span>
  </div>
</template>

<script>
import Util from '@/mixins/Util'

export default {
  name: 'StudentWithdrawalCancel',
  mixins: [Util],
  props: {
    termId: {
      required: false,
      default: undefined,
      type: String
    },
    withdrawal: {
      required: true,
      type: Object
    }
  }
}
</script>
