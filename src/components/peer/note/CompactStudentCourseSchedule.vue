<template>
  <div class="mb-1 text-center w-100">
    <v-btn
      id="show-hide-student-enrollments"
      aria-controls="student-enrollments"
      :aria-expanded="isExpanded"
      :aria-label="`Course schedule of ${studentName}`"
      class="text-no-wrap"
      color="primary"
      variant="text"
      @click="() => isExpanded = !isExpanded"
    >
      <div class="align-center d-flex">
        <v-icon :icon="isExpanded ? mdiMenuDown : mdiMenuRight" size="24" />
        <div>
          {{ isExpanded ? 'Hide' : 'Show' }} {{ studentName }}'s course schedule
        </div>
      </div>
    </v-btn>
  </div>
  <v-expand-transition>
    <div
      v-if="isExpanded && terms"
      id="student-enrollments"
      class="d-flex flex-wrap"
    >
      <div
        v-for="term of terms"
        :key="term.termId"
        style="width: 33%"
      >
        <table>
          <thead>
            <tr>
              <th class="border-b-md text-medium-emphasis">
                {{ term.termName }}
              </th>
              <th class="border-b-md text-medium-emphasis">
                Units
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(enrollemnt, index) in term.enrollments" :key="index">
              <td>
                {{ enrollemnt.displayName }}
              </td>
              <td>
                {{ enrollemnt.units }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </v-expand-transition>
</template>

<script setup lang="ts">
import {isNil} from 'lodash'
import {mdiMenuDown, mdiMenuRight} from '@mdi/js'
import {ref, watch} from 'vue'
import type {TermEnrollment} from '@/lib/types'
import {getStudentEnrollments} from '@/api/peer-advising'

const props = defineProps({
  sid: {
    required: true,
    type: String
  },
  studentName: {
    required: true,
    type: String
  }
})

const terms = ref<TermEnrollment[] | undefined>()
const isExpanded = ref(false)

watch(isExpanded, value => {
  if (value && isNil(terms.value)) {
    getStudentEnrollments(props.sid).then(data => {
      terms.value = data
    })
  }
})
</script>
