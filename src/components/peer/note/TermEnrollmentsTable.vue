<template>
  <table class="w-100">
    <thead>
      <tr>
        <th class="border-b-md pb-1 text-medium-emphasis text-no-wrap text-medium-emphasis w-66">
          {{ termNameForSisId(termId) }}
        </th>
        <th v-if="size(enrollments)" class="border-b-md pb-1 text-medium-emphasis text-right text-medium-emphasis w-33">
          {{ totalUnits }} Units <span class="sr-only">total</span>
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
            <template v-if="enrollment.sections.some(s => s.isUncompletedPerGrade)">
              <v-icon
                :id="`student-${studentUid}-non-completed-course-${termId}-${normalizeId(enrollment.displayName)}`"
                color="warning"
                :icon="mdiAlert"
                size="20"
                title="Non-completed course"
              />
              <span class="sr-only">Not completed by this student</span>
            </template>
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
          {{ enrollment.units }} <span class="sr-only">units</span>
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
import {computed} from 'vue'
import {filter as _filter, map, size} from 'lodash'
import {mdiAlert} from '@mdi/js'
import type {Enrollment, Section} from '@/lib/types'
import {normalizeId} from '@/lib/utils'
import {termNameForSisId} from '@/lib/berkeley-utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
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

const totalUnits = computed(() =>
  (props.enrollments ?? []).reduce((sum, e) => sum + (Number(e?.units) || 0), 0)
)
const getWaitlistedSections = (enrollment: Enrollment): Section[] => {
  return _filter(enrollment.sections, ['enrollmentStatus', 'W'])
}
</script>
