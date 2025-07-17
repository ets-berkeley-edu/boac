<template>
  <div>
    <div v-if="eForm.term" class="mb-3">
      <dt class="font-weight-bold">Term</dt>
      <dd>{{ termNameForSisId(eForm.term) }}</dd>
    </div>
    <div class="mb-3">
      <dt class="font-weight-bold">Course</dt>
      <dd>{{ eForm.sectionId }} {{ eForm.courseName }} - {{ eForm.courseTitle }} {{ eForm.section }}</dd>
    </div>
    <div class="mb-3">
      <dt class="font-weight-bold">Action</dt>
      <dd>
        {{ eForm.action }}
        <span v-if="eForm.action === 'Late Grading Basis Change' && eForm.gradingBasis"> from <span class="font-italic">{{ eForm.gradingBasis }}</span></span>
        <span v-if="eForm.action === 'Late Grading Basis Change' && eForm.requestedGradingBasis"> to <span class="font-italic">{{ eForm.requestedGradingBasis }}</span></span>
        <span v-if="eForm.action === 'Unit Change' && eForm.unitsTaken"> from <span class="font-italic">{{ numFormat(eForm.unitsTaken, '0.0') }}</span>{{ 1 === toInt(eForm.unitsTaken) ? ' unit' : ' units' }}</span>
        <span v-if="eForm.action === 'Unit Change' && eForm.requestedUnitsTaken"> to <span class="font-italic">{{ numFormat(eForm.requestedUnitsTaken, '0.0') }}</span>{{ 1 === toInt(eForm.requestedUnitsTaken) ? ' unit' : ' units' }}</span>
      </dd>
    </div>
  </div>
</template>

<script setup lang="ts">
import {numFormat, toInt} from '@/lib/utils'
import {termNameForSisId} from '@/lib/berkeley-utils'

defineProps({
  eForm: {
    required: true,
    type: Object
  }
})
</script>
