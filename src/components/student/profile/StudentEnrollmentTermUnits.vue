<template>
  <div class="pt-3 student-term-footer">
    <div class="d-flex justify-space-between">
      <div :id="`term-${term.termId}-gpa`">
        <span class="student-course-label">Term GPA: </span>
        <span
          v-if="round(get(term, 'termGpa.gpa', 0), 3) > 0"
          class="font-size-14"
        >
          {{ round(get(term, 'termGpa.gpa', 0), 3) }}
        </span>
        <span v-else>&mdash;</span>
      </div>
      <div :id="`term-${term.termId}-units`" class="align-center d-flex justify-content-end">
        <div class="student-course-label align-right">Total Units: </div>
        <div class="font-size-14 text-right" :class="{'units-total': showMinUnits || showMaxUnits}">
          <span v-if="get(term, 'enrolledUnits', 0) !== 0">{{ numFormat(term.enrolledUnits, '0.0') }}</span>
          <span v-else>&mdash;</span>
        </div>
      </div>
    </div>
    <div
      v-if="showMinUnits || showMaxUnits"
      :id="`term-${term.termId}-units-allowed`"
      class="text-right"
    >
      <div v-if="showMinUnits" class="align-center d-flex justify-content-end">
        <div class="student-course-label align-right">Exception Min Units: </div>
        <div :id="`term-${term.termId}-min-units`" class="font-size-14 units-total">
          {{ numFormat(term.minTermUnitsAllowed, '0.0') || '&mdash;' }}
        </div>
      </div>
      <div v-if="showMaxUnits" class="align-center d-flex justify-content-end">
        <div class="student-course-label align-right">Exception Max Units: </div>
        <div :id="`term-${term.termId}-max-units`" class="font-size-14 units-total">
          {{ numFormat(term.maxTermUnitsAllowed, '0.0') || '&mdash;' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {get, isNil} from 'lodash'
import {numFormat, round} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  term: {
    required: true,
    type: Object
  }
})
const config = useContextStore().config
const maxUnits = props.term.maxTermUnitsAllowed
const minUnits = props.term.minTermUnitsAllowed
const showMaxUnits = isNil(maxUnits) && maxUnits !== config.defaultTermUnitsAllowed.max
const showMinUnits = !isNil(minUnits) && minUnits !== config.defaultTermUnitsAllowed.min
</script>

<style scoped>
.student-term-footer {
  border-top: 1px #999 solid !important;
}
.units-total {
  min-width: 30px;
}
</style>
