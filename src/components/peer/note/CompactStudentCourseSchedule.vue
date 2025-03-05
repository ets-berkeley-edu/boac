<template>
  <div :class="{'mb-3': !isExpanded || isFetching}" class="w-100">
    <v-btn
      id="show-hide-student-enrollments"
      aria-controls="student-enrollments"
      :aria-expanded="isExpanded"
      class="font-size-15 px-1 text-no-wrap"
      color="primary"
      density="compact"
      variant="text"
      @click="() => isExpanded = !isExpanded"
    >
      <div class="align-center d-flex">
        <v-progress-circular
          v-if="isFetching"
          class="ml-2 mr-1"
          indeterminate
          size="14"
          width="2"
        />
        <v-icon v-if="!isFetching" :icon="isExpanded ? mdiMenuDown : mdiMenuRight" size="24" />
        <div>
          {{ isExpanded ? 'Hide' : 'Show' }} {{ student.firstName }}'s course schedule
        </div>
      </div>
    </v-btn>
  </div>
  <v-expand-transition id="student-enrollments">
    <div v-if="isExpanded && terms" class="border-sm mt-3 mx-2 pl-3 pt-3">
      <h4 class="mb-2 text-medium-emphasis">Course Schedule</h4>
      <div class="d-flex flex-wrap">
        <div
          v-for="term of terms"
          :key="term.termId"
          class="mb-4"
          style="width: 33%"
        >
          <table class="w-90">
            <thead>
              <tr>
                <th class="border-b-md pb-1 text-medium-emphasis text-no-wrap text-grey">
                  {{ term.termName }}
                </th>
                <th class="border-b-md pb-1 text-medium-emphasis text-right text-grey">
                  Units
                </th>
              </tr>
            </thead>
            <tbody v-if="size(term.enrollments)">
              <tr v-for="(enrollment, index) in term.enrollments" :key="index">
                <td :class="{'pt-1': index === 0}" class="font-size-12 font-weight-bold">
                  {{ enrollment.displayName }}
                </td>
                <td :class="{'pt-1': index === 0}" class="text-right">
                  {{ enrollment.units }}
                </td>
              </tr>
            </tbody>
            <tbody v-if="!size(term.enrollments)">
              <tr>
                <td class="font-italic font-size-14 pt-2 text-medium-emphasis">No {{ term.termName }} enrollments</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </v-expand-transition>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {isNil, size} from 'lodash'
import {mdiMenuDown, mdiMenuRight} from '@mdi/js'
import {ref, watch} from 'vue'
import type {HasName, TermEnrollment} from '@/lib/types'
import {getStudentEnrollments} from '@/api/peer-advising'

const props = defineProps({
  sid: {
    required: true,
    type: String
  },
  student: {
    required: true,
    type: Object as PropType<HasName>
  }
})

const terms = ref<TermEnrollment[] | undefined>()
const isExpanded = ref(false)
const isFetching = ref(false)

watch(isExpanded, value => {
  if (value && isNil(terms.value)) {
    isFetching.value = true
    getStudentEnrollments(props.sid).then(data => {
      terms.value = data
      isFetching.value = false
    })
  }
})
</script>
