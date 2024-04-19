<template>
  <div v-if="!termId || toInt(withdrawal.termId) === toInt(termId)">
    <span :id="`withdrawal-term-${termId}`" class="text-error font-weight-bold">
      {{ withdrawal.description }}
      ({{ withdrawal.reason }})
      <span v-if="withdrawalDate" class="text-no-wrap">{{ withdrawalDate.toFormat('DD') }}</span>
    </span>
  </div>
</template>

<script setup>
import {DateTime} from 'luxon'
import {toInt} from '@/lib/utils'

const props = defineProps({
  termId: {
    required: false,
    default: undefined,
    type: String
  },
  withdrawal: {
    required: true,
    type: Object
  }
})

const termId = props.termId
const withdrawal = props.withdrawal
const withdrawalDate = DateTime.fromSQL(withdrawal.date)
</script>
