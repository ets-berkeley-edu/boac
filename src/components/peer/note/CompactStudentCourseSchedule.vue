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
    <div v-if="isExpanded && academicYears" class="border-sm ma-2 pl-4 py-3">
      <h4 class="mb-2 text-medium-emphasis">Course Schedule</h4>
      <div
        v-for="(academicYear, label, index) of academicYears"
        :key="label"
      >
        <h5 class="sr-only">{{ label }}</h5>
        <div :class="{'mt-5': index}" class="align-start d-flex justify-space-between">
          <div
            v-for="(enrollments, termId) in academicYear"
            :key="termId"
            class="mr-5"
            :class="{
              'bg-pale-yellow elevation-1 pb-2 pt-1 px-3': currentEnrollmentTermId === termId.toString(),
              'pt-1': currentEnrollmentTermId !== termId.toString()
            }"
            style="width: 33%"
          >
            <TermEnrollmentsTable
              :enrollments="enrollments"
              :student-uid="student.uid"
              :term-id="termId"
            />
          </div>
        </div>
      </div>
    </div>
  </v-expand-transition>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {isNil} from 'lodash'
import {mdiMenuDown, mdiMenuRight} from '@mdi/js'
import {ref, watch} from 'vue'
import type {BasicStudent, Enrollment} from '@/lib/types'
import TermEnrollmentsTable from '@/components/peer/note/TermEnrollmentsTable.vue'
import {getStudentEnrollments} from '@/api/peer-advising'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  student: {
    required: true,
    type: Object as PropType<BasicStudent>
  }
})

const contextStore = useContextStore()
const currentEnrollmentTermId = contextStore.config.currentEnrollmentTermId.toString()
const currentUser = contextStore.currentUser
const isExpanded = ref(false)
const isFetching = ref(false)
const academicYears = ref<Map<string, Map<string, Enrollment[]>> | undefined>()

watch(isExpanded, value => {
  if (value && isNil(academicYears.value)) {
    isFetching.value = true
    getStudentEnrollments(props.student.sid).then(data => {
      academicYears.value = data
      isFetching.value = false
    })
  }
})
</script>
