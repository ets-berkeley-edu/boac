<template>
  <table class="w-100">
    <thead>
      <tr>
        <th class="border-b-md pb-1 text-medium-emphasis text-no-wrap text-grey">
          {{ termNameForSisId(termId) }}
        </th>
        <th v-if="size(enrollments)" class="border-b-md pb-1 text-medium-emphasis text-right text-grey">
          Units
        </th>
      </tr>
    </thead>
    <tbody v-if="size(enrollments)">
      <tr v-for="(enrollment, index) in enrollments" :key="enrollment.displayName" class="font-size-13">
        <td
          :class="{'demo-mode-blur': currentUser.inDemoMode, 'pt-1': index === 0}"
          class="font-weight-bold text-medium-emphasis"
        >
          <div class="align-center d-flex">
            <div class="mr-1">
              {{ enrollment.displayName }}
            </div>
            <v-icon
              v-if="enrollment.sections.some(s => s.isUncompletedPerGrade)"
              :id="`student-${studentUid}-uncompleted-course-${termId}-${normalizeId(enrollment.displayName)}`"
              :aria-label="`${enrollment.displayName} course was uncompleted by this student`"
              color="warning"
              :icon="mdiAlert"
              size="20"
              title="Uncompleted course"
            />
          </div>
          <div
            v-if="getWaitlistedSections(enrollment).length"
            :id="`student-${studentUid}-waitlisted-for-${termId}-${normalizeId(enrollment.displayName)}`"
            class="font-weight-bolder mb-1 ml-1 text-error text-uppercase"
          >
            Waitlisted<span v-if="getWaitlistedSections(enrollment).length > 1">:
              <span :class="{'demo-mode-blur': currentUser.inDemoMode}">
                Sections {{ map(getWaitlistedSections(enrollment), s => s.sectionNumber).join(', ') }}
              </span>
            </span>
          </div>
        </td>
        <td :class="{'pt-1': index === 0}" class="text-right vertical-top">
          {{ enrollment.units }}
        </td>
      </tr>
    </tbody>
    <tbody v-if="!size(enrollments)">
      <tr>
        <td class="font-italic font-size-13 pt-2 text-medium-emphasis">No enrollments</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {filter as _filter, map, size} from 'lodash'
import {mdiAlert} from '@mdi/js'
import type {Enrollment, Section} from '@/lib/types'
import {normalizeId} from '@/lib/utils'
import {termNameForSisId} from '@/lib/berkeley-utils'
import {useContextStore} from '@/stores/context'

defineProps({
  enrollments: {
    required: true,
    type: Array as PropType<Enrollment[]>
  },
  studentUid: {
    required: true,
    type: String
  },
  termId: {
    required: true,
    type: String
  }
})

const currentUser = useContextStore().currentUser

const getWaitlistedSections = (enrollment: Enrollment): Section[] => {
  return _filter(enrollment.sections, ['enrollmentStatus', 'W'])
}
</script>
