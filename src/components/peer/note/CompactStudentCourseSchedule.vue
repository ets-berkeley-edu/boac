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
          {{ isExpanded ? 'Hide' : 'Show' }} <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.firstName }}</span>'s course schedule
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
              <tr v-for="(enrollment, index) in term.enrollments" :key="index" class="font-size-13">
                <td
                  :class="{'demo-mode-blur': currentUser.inDemoMode, 'pt-1': index === 0}"
                  class="font-weight-bold text-medium-emphasis"
                >
                  {{ enrollment.displayName }}
                  <div
                    v-if="getWaitlistedSections(enrollment).length"
                    :id="`student-${student.uid}-waitlisted-for-${term.termId}-${normalizeId(enrollment.displayName)}`"
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
import {filter as _filter, isNil, map, size} from 'lodash'
import {mdiMenuDown, mdiMenuRight} from '@mdi/js'
import {ref, watch} from 'vue'
import type {BasicStudent, Enrollment, Section, TermEnrollment} from '@/lib/types'
import {getStudentEnrollments} from '@/api/peer-advising'
import {normalizeId} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  student: {
    required: true,
    type: Object as PropType<BasicStudent>
  }
})

const currentUser = useContextStore().currentUser
const isExpanded = ref(false)
const isFetching = ref(false)
const terms = ref<TermEnrollment[] | undefined>()

watch(isExpanded, value => {
  if (value && isNil(terms.value)) {
    isFetching.value = true
    getStudentEnrollments(props.student.sid).then(data => {
      terms.value = data
      isFetching.value = false
    })
  }
})

const getWaitlistedSections = (enrollment: Enrollment): Section[] => {
  return _filter(enrollment.sections, ['enrollmentStatus', 'W'])
}
</script>
