<template>
  <div v-if="!termId || toInt(withdrawal.termId) === toInt(termId)">
    <span :id="`withdrawal-term-${termId}`" class="error font-weight-bold">
      {{ withdrawal.description }}
      ({{ withdrawal.reason }})
      <span class="text-no-wrap">{{ DateTime.fromJSDate(withdrawal.date).toFormat('MMM DD, YYYY') }}</span>
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
