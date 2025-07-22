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
      <dd class="ml-2 mt-1">
        <table class="w-100">
          <tr v-if="eForm.lastUserName">
            <th class="font-weight-bold pr-5 pt-1 text-left text-medium-emphasis vertical-top" scope="row">
              Advisor:
            </th>
            <td :id="`note-${noteId}-eform-advisor`" class="pt-1 vertical-bottom">{{ replace(eForm.lastUserName, ',', ', ') }} ({{ eForm.lastUserUid }})</td>
          </tr>
          <tr v-if="eForm.originalUserName">
            <th class="font-weight-bold pr-5 pt-1 text-left text-medium-emphasis vertical-top" scope="row">
              DSP Specialist:
            </th>
            <td :id="`note-${noteId}-eform-dsp-specialist`" class="pt-1 vertical-bottom">{{ replace(eForm.originalUserName, ',', ', ') }}</td>
          </tr>
        </table>
      </dd>
    </div>
    <div v-if="eForm.requestedReducedUnits || eForm.termEnrolledUnits || eForm.termWaitlistUnits" class="mt-3">
      <dt class="font-weight-bold">Units ({{ termNameForSisId(eForm.termId) }})</dt>
      <dd class="ml-2 mt-1">
        <table class="w-100">
          <tr v-if="eForm.termEnrolledUnits" :id="`note-${noteId}-eform-term-enrolled-units`">
            <th class="font-weight-bold pr-5 pt-1 text-left text-medium-emphasis vertical-top" scope="row">
              Enrolled Units (at time of submission):
            </th>
            <td class="pt-1 text-right vertical-bottom">{{ numeral(eForm.termEnrolledUnits).format('0.0') }}</td>
          </tr>
          <tr v-if="eForm.requestedReducedUnits" :id="`note-${noteId}-eform-requested-reduced-units`">
            <th class="font-weight-bold pr-5 pt-1 text-left text-medium-emphasis vertical-top" scope="row">
              Requested Reduced Units:
            </th>
            <td class="pt-1 text-right vertical-bottom">{{ numeral(eForm.requestedReducedUnits).format('0.0') }}</td>
          </tr>
          <tr v-if="eForm.termWaitlistUnits" :id="`note-${noteId}-eform-term-waitlist-units`">
            <th class="font-weight-bold pr-5 pt-1 text-left text-medium-emphasis vertical-top" scope="row">
              Waitlist Units:
            </th>
            <td class="pt-1 text-right vertical-bottom">{{ numeral(eForm.termWaitlistUnits).format('0.0') }}</td>
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
