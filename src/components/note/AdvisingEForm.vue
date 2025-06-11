<template>
  <dl :id="`note-${note.id}-message-open`">
    <div v-if="note.eForm.dataSource === 'student_cpp_change_eforms'">
      <div v-if="trim(note.eForm.type)" class="mb-3">
        <dt class="font-weight-bold">eForm Type</dt>
        <dd>
          {{ note.eForm.type }}
        </dd>
      </div>
      <div v-if="note.eForm.academicProgramName" class="mb-3">
        <dt class="font-weight-bold">Academic Program</dt>
        <dd :id="`note-${note.id}-eform-program-name`">
          {{ note.eForm.academicProgramName }} ({{ note.eForm.academicCareerCode }})
          <span v-if="note.eForm.toAcademicProgramName">(requesting {{ note.eForm.toAcademicProgramName }}.</span>
        </dd>
      </div>
      <div v-if="note.eForm.degreeExpectedTermId" class="mb-3">
        <dt class="font-weight-bold">Expected Graduation Term</dt>
        <dd>
          {{ termNameForSisId(note.eForm.degreeExpectedTermId) }}
          <span v-if="note.eForm.toDegreeExpectedTermId">(requesting {{ termNameForSisId(note.eForm.toDegreeExpectedTermId) }})</span>
        </dd>
      </div>
      <div v-if="note.eForm.academicPlanName" class="mb-3">
        <dt class="font-weight-bold">Academic Plan</dt>
        <dd :id="`note-${note.id}-eform-academic-plan-name`">
          {{ note.eForm.academicPlanName }}
          <span v-if="note.eForm.academicPlanTypeDescription">({{ note.eForm.academicPlanTypeDescription }})</span>
          <span v-if="note.eForm.toAcademicPlanName">and is requesting {{ note.eForm.toAcademicPlanName }}.</span>
        </dd>
      </div>
      <div v-if="note.eForm.academicSubplanName" class="mb-3">
        <dt class="font-weight-bold">Academic Subplan</dt>
        <dd :id="`note-${note.id}-eform-academic-subplan-name`">
          {{ note.eForm.academicSubplanName }}
          <span v-if="note.eForm.toAcademicSubplanName">(requesting {{ note.eForm.toAcademicSubplanName }}<span v-if="note.eForm.toAcademicSubplanRequirementTermId"> for {{ note.eForm.toAcademicSubplanRequirementTermId }}</span>)</span>
        </dd>
      </div>
      <div v-if="note.eForm.overlapCourses.length" class="mb-3">
        <dt class="font-weight-bold">Overlap Course{{ note.eForm.overlapCourses.length === 1 ? '' : 's' }}</dt>
        <dd :id="`note-${note.id}-eform-overlap-courses`">
          <ul class="ml-5">
            <li
              v-for="(overlapCourse, index) in note.eForm.overlapCourses"
              :key="index"
            >
              {{ overlapCourse }}
            </li>
          </ul>
        </dd>
      </div>
    </div>
    <div v-if="note.eForm.dataSource === 'student_late_drop_eforms'">
      <div class="mb-3">
        <dt class="font-weight-bold">Course</dt>
        <dd>{{ note.eForm.sectionId }} {{ note.eForm.courseName }} - {{ note.eForm.courseTitle }} {{ note.eForm.section }}</dd>
      </div>
      <div class="mb-3">
        <dt class="font-weight-bold">Action</dt>
        <dd>
          {{ note.eForm.action }}
          <span v-if="note.eForm.action === 'Late Grading Basis Change' && note.eForm.gradingBasis"> from <span class="font-italic">{{ note.eForm.gradingBasis }}</span></span>
          <span v-if="note.eForm.action === 'Late Grading Basis Change' && note.eForm.requestedGradingBasis"> to <span class="font-italic">{{ note.eForm.requestedGradingBasis }}</span></span>
          <span v-if="note.eForm.action === 'Unit Change' && note.eForm.unitsTaken"> from <span class="font-italic">{{ numFormat(note.eForm.unitsTaken, '0.0') }}</span>{{ 1 === toInt(note.eForm.unitsTaken) ? ' unit' : ' units' }}</span>
          <span v-if="note.eForm.action === 'Unit Change' && note.eForm.requestedUnitsTaken"> to <span class="font-italic">{{ numFormat(note.eForm.requestedUnitsTaken, '0.0') }}</span>{{ 1 === toInt(note.eForm.requestedUnitsTaken) ? ' unit' : ' units' }}</span>
        </dd>
      </div>
    </div>
    <div class="mb-3">
      <dt class="font-weight-bold">Form ID</dt>
      <dd>{{ note.eForm.id }}</dd>
    </div>
    <div class="mb-3">
      <dt class="font-weight-bold">Date Initiated</dt>
      <dd>{{ DateTime.fromISO(note.createdAt).toFormat('MM/dd/yyyy') }}</dd>
    </div>
    <div class="mb-3">
      <dt class="font-weight-bold">Form Status </dt>
      <dd>{{ note.eForm.status }}</dd>
    </div>
    <div v-if="note.eForm.dataSource === 'student_late_drop_eforms'" class="mb-3">
      <dt class="font-weight-bold">Final Date &amp; Time Stamp</dt>
      <dd>{{ DateTime.fromISO(note.updatedAt).toFormat('MM/dd/yyyy h:mm:ssa') }}</dd>
    </div>
    <div v-if="note.eForm.dataSource !== 'student_late_drop_eforms'" class="mb-3">
      <dt class="font-weight-bold">Last Updated</dt>
      <dd>{{ DateTime.fromISO(note.updatedAt).toFormat('MM/dd/yyyy') }}</dd>
    </div>
  </dl>
</template>

<script setup lang="ts">
import {DateTime} from 'luxon'
import {trim} from 'lodash'
import {numFormat, toInt} from '@/lib/utils'
import {termNameForSisId} from '@/lib/berkeley-utils'

defineProps({
  note: {
    required: true,
    type: Object
  }
})
</script>
