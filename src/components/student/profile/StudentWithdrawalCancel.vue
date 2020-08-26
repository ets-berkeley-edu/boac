<template>
  <div v-if="!termId || toInt(withdrawal.termId) === toInt(termId)">
    <span :id="`withdrawal-term-${termId}`" class="red-flag-small">
      {{ withdrawal.description }}
      ({{ withdrawal.reason }})
      {{ withdrawal.date | moment('MMM DD, YYYY') }}
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
      type: [String, Number]
    },
    withdrawal: {
      required: true,
      type: Object
    }
  }
}
</script>
