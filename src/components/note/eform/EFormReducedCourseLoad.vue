<template>
  <div>
    <div v-if="eForm.type" class="mt-3">
      <dt class="font-weight-bold">eForm Type</dt>
      <dd :id="`note-${noteId}-eform-type`">
        {{ eForm.type }}
      </dd>
    </div>
    <div v-if="eForm.academicStandingDescription" class="mt-3">
      <dt class="font-weight-bold">Academic Standing</dt>
      <dd>
        {{ eForm.academicStandingDescription }}<span v-if="eForm.academicStandingStatus"> ({{ eForm.academicStandingStatus }})</span>
      </dd>
    </div>
    <div v-if="eForm.lastUserName || eForm.originalUserName" class="mt-3">
      <dt class="font-weight-bold">Staff</dt>
      <dd class="ml-2 mt-2">
        <table>
          <tr v-if="eForm.lastUserName" class="mt-1">
            <td class="font-weight-bold pr-5 text-grey-darken-1">Advisor:</td>
            <td :id="`note-${noteId}-eform-advisor`" class="float-right">{{ replace(eForm.lastUserName, ',', ', ') }} ({{ eForm.lastUserUid }})</td>
          </tr>
          <tr v-if="eForm.originalUserName">
            <td class="font-weight-bold pr-5 text-grey-darken-1">DSP Specialist:</td>
            <td :id="`note-${noteId}-eform-dsp-specialist`" class="float-right">{{ replace(eForm.originalUserName, ',', ', ') }}</td>
          </tr>
        </table>
      </dd>
    </div>

    <div v-if="eForm.requestedReducedUnits || eForm.termEnrolledUnits || eForm.termWaitlistUnits" class="mt-3">
      <dt class="font-weight-bold">Units ({{ termNameForSisId(eForm.termId) }})</dt>
      <dd class="ml-2 mt-2">
        <table>
          <tr v-if="eForm.termEnrolledUnits" :id="`note-${noteId}-eform-term-enrolled-units`">
            <td class="font-weight-bold pr-5 text-grey-darken-1">Enrolled Units:</td>
            <td class="float-right">{{ numeral(eForm.termEnrolledUnits).format('0.0') }}</td>
          </tr>
          <tr v-if="eForm.requestedReducedUnits" :id="`note-${noteId}-eform-requested-reduced-units`">
            <td class="font-weight-bold pr-5 text-grey-darken-1">Requested Reduced Units:</td>
            <td class="float-right">{{ numeral(eForm.requestedReducedUnits).format('0.0') }}</td>
          </tr>
          <tr v-if="eForm.termWaitlistUnits" :id="`note-${noteId}-eform-term-waitlist-units`">
            <td class="font-weight-bold pr-5 text-grey-darken-1">Waitlist Units:</td>
            <td class="float-right">{{ numeral(eForm.termWaitlistUnits).format('0.0') }}</td>
          </tr>
        </table>
      </dd>
    </div>
  </div>
</template>

<script setup lang="ts">
import numeral from 'numeral'
import {replace} from 'lodash'
import {termNameForSisId} from '@/lib/berkeley-utils'

defineProps({
  eForm: {
    required: true,
    type: Object
  },
  noteId: {
    required: true,
    type: String
  }
})
</script>
