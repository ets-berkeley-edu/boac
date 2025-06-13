<template>
  <div>
    <div v-if="eForm.type" class="mt-3">
      <dt class="font-weight-bold">eForm Type</dt>
      <dd>
        {{ eForm.type }}
      </dd>
    </div>
    <div v-if="eForm.academicProgramName" class="mt-3">
      <dt class="font-weight-bold">Academic Program</dt>
      <dd :id="`note-${noteId}-eform-program-name`">
        {{ eForm.academicProgramName }} ({{ eForm.academicCareerCode }})
        <span v-if="eForm.toAcademicProgramName">(requesting {{ eForm.toAcademicProgramName }}.</span>
      </dd>
    </div>
    <div v-if="eForm.degreeExpectedTermId" class="mt-3">
      <dt class="font-weight-bold">Expected Graduation Term</dt>
      <dd>
        {{ termNameForSisId(eForm.degreeExpectedTermId) }}
        <span v-if="eForm.toDegreeExpectedTermId">(requesting {{ termNameForSisId(eForm.toDegreeExpectedTermId) }})</span>
      </dd>
    </div>
    <div v-if="eForm.academicPlanName" class="mt-3">
      <dt class="font-weight-bold">Academic Plan</dt>
      <dd :id="`note-${noteId}-eform-academic-plan-name`">
        {{ eForm.academicPlanName }}
        <span v-if="eForm.academicPlanTypeDescription">({{ eForm.academicPlanTypeDescription }})</span>
        <span v-if="eForm.toAcademicPlanName">and is requesting {{ eForm.toAcademicPlanName }}.</span>
      </dd>
    </div>
    <div v-if="eForm.academicSubplanName" class="mt-3">
      <dt class="font-weight-bold">Academic Subplan</dt>
      <dd :id="`note-${noteId}-eform-academic-subplan-name`">
        {{ eForm.academicSubplanName }}
        <span v-if="eForm.toAcademicSubplanName">(requesting {{ eForm.toAcademicSubplanName }}<span v-if="eForm.toAcademicSubplanRequirementTermId"> for {{ eForm.toAcademicSubplanRequirementTermId }}</span>)</span>
      </dd>
    </div>
    <div v-if="eForm.overlapCourses.length" class="mt-3">
      <dt class="font-weight-bold">Overlap Course{{ eForm.overlapCourses.length === 1 ? '' : 's' }}</dt>
      <dd :id="`note-${noteId}-eform-overlap-courses`">
        <ul class="ml-5">
          <li
            v-for="(overlapCourse, index) in eForm.overlapCourses"
            :key="index"
          >
            {{ overlapCourse }}
          </li>
        </ul>
      </dd>
    </div>
  </div>
</template>

<script setup lang="ts">
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
